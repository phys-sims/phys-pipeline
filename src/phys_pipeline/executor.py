from __future__ import annotations

import time
from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from .accumulator import RunAccumulator
from .dag import build_dag
from .dag_cache import DagCache
from .errors import SchedulerRetryError, SchedulerTimeoutError
from .hashing import hash_dag_node, hash_model, hash_policy, hash_state
from .ml_artifacts import ModelArtifactPackager
from .policy import PolicyLike, as_policy
from .record import ArtifactRecorder
from .scheduler import LocalScheduler, Scheduler
from .types import DagState, NodeSpec, StageResult, State


class MpiRunner(Protocol):
    def run(self, stage: Any, state: State, *, resources: Any) -> StageResult[State]: ...


@dataclass(slots=True)
class RetryPolicy:
    max_retries: int = 0
    timeout_s: float | None = None
    backoff_s: float = 0.0


@dataclass(slots=True)
class NodeProvenance:
    node_id: str
    started_at: float
    finished_at: float
    attempts: int
    cache_hit: bool = False
    error: str | None = None


@dataclass
class DagRunResult:
    results: dict[str, StageResult[State]]
    metrics: dict[str, float]
    artifacts: dict[str, Any]
    provenance: dict[str, Any]
    execution_order: list[str] = field(default_factory=list)


class DagExecutor:
    """Execute DAG nodes with optional scheduling, caching, and retries."""

    def __init__(
        self,
        *,
        scheduler: Scheduler | None = None,
        cache: DagCache | None = None,
        retry_policy: RetryPolicy | None = None,
        policy: PolicyLike | None = None,
        mpi_runner: MpiRunner | None = None,
        model_packager: ModelArtifactPackager | None = None,
    ):
        self.scheduler = scheduler or LocalScheduler(max_workers=1, max_cpu=1, max_gpu=0)
        self.cache = cache
        self.retry_policy = retry_policy or RetryPolicy()
        self.policy = as_policy(policy)
        self.mpi_runner = mpi_runner
        self.model_packager = model_packager

    def set_policy(self, policy: PolicyLike | None) -> None:
        self.policy = as_policy(policy)

    def run(
        self,
        initial_state: State,
        nodes: list[NodeSpec],
        *,
        record_artifacts: bool = False,
        recorder: ArtifactRecorder | None = None,
        policy: PolicyLike | None = None,
    ) -> DagRunResult:
        run_policy = as_policy(policy) if policy is not None else self.policy
        policy_hash = hash_policy(run_policy) if run_policy is not None else None
        dag = build_dag(nodes)
        results: dict[str, StageResult[State]] = {}
        provenance_records: list[NodeProvenance] = []

        acc = RunAccumulator(
            record_artifacts=record_artifacts,
            recorder=recorder,
            ns_stack=[],
        )
        if policy_hash is not None:
            acc.provenance["policy_hash"] = policy_hash

        in_degree = {node_id: len(deps) for node_id, deps in dag.deps.items()}
        ready = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        running: dict[str, Any] = {}
        attempts: dict[str, int] = {node_id: 0 for node_id in dag.nodes_by_id}
        execution_order: list[str] = []

        def build_input_state(node_id: str) -> State:
            deps = dag.deps[node_id]
            if not deps:
                return initial_state
            if len(deps) == 1:
                return results[deps[0]].state
            return DagState({dep: results[dep].state for dep in deps})

        def compute_cache_key(node: NodeSpec, input_state: State) -> str:
            dep_hashes = {dep: hash_state(results[dep].state) for dep in dag.deps[node.id]}
            cfg_hash = None
            stage = node.stage
            if stage is not None and getattr(stage, "cfg", None) is not None:
                try:
                    cfg_hash = hash_model(stage.cfg)
                except Exception:
                    cfg_hash = None
            return hash_dag_node(
                node_id=node.id,
                op_name=node.op_name or node.id,
                version=node.version or "v2",
                cfg_hash=cfg_hash,
                input_hash=hash_state(input_state),
                dep_hashes=dep_hashes,
                policy_hash=policy_hash,
            )

        def run_node(node: NodeSpec, input_state: State) -> StageResult[State]:
            if node.stage is None:
                raise ValueError(f"Node '{node.id}' has no stage attached.")
            if node.resources.mpi_ranks > 1 and self.mpi_runner is not None:
                return self.mpi_runner.run(node.stage, input_state, resources=node.resources)
            return node.stage.process(input_state, policy=run_policy)

        while ready or running:
            while ready:
                node_id = ready.popleft()
                node = dag.nodes_by_id[node_id]
                input_state = build_input_state(node_id)
                cache_key = compute_cache_key(node, input_state)
                if self.cache is not None:
                    cached = self.cache.get(cache_key)
                    if cached is not None:
                        result = StageResult(
                            state=cached.state,
                            metrics=cached.metrics,
                            provenance=cached.provenance,
                        )
                        acc.consume(node.id, result)
                        results[node_id] = result
                        provenance_records.append(
                            NodeProvenance(
                                node_id=node_id,
                                started_at=time.time(),
                                finished_at=time.time(),
                                attempts=attempts[node_id],
                                cache_hit=True,
                            )
                        )
                        execution_order.append(node_id)
                        for dependent in dag.reverse_deps[node_id]:
                            in_degree[dependent] -= 1
                            if in_degree[dependent] == 0:
                                ready.append(dependent)
                        continue

                def _run(n: NodeSpec = node, st: State = input_state) -> StageResult[State]:
                    return run_node(n, st)

                attempts[node_id] += 1
                handle = self.scheduler.submit(
                    node_id,
                    _run,
                    node.resources,
                    attempt=attempts[node_id],
                )
                running[node_id] = {
                    "handle": handle,
                    "node": node,
                    "input_state": input_state,
                    "cache_key": cache_key,
                    "started_at": time.time(),
                }

            if not running:
                continue

            try:
                handle = self.scheduler.wait_any(
                    [payload["handle"] for payload in running.values()],
                    timeout_s=self.retry_policy.timeout_s,
                )
            except SchedulerTimeoutError as exc:
                raise SchedulerTimeoutError(str(exc)) from exc
            node_id = handle.node_id
            payload = running.pop(node_id)
            node = payload["node"]
            started_at = payload["started_at"]

            try:
                result = handle.future.result(timeout=self.retry_policy.timeout_s)
            except Exception as exc:
                if attempts[node_id] <= self.retry_policy.max_retries:
                    time.sleep(self.retry_policy.backoff_s)
                    attempts[node_id] += 1

                    def _retry(
                        n: NodeSpec = node, st: State = payload["input_state"]
                    ) -> StageResult[State]:
                        return run_node(n, st)

                    handle = self.scheduler.submit(
                        node_id,
                        _retry,
                        node.resources,
                        attempt=attempts[node_id],
                    )
                    running[node_id] = {**payload, "handle": handle}
                    continue
                error_msg = str(exc)
                provenance_records.append(
                    NodeProvenance(
                        node_id=node_id,
                        started_at=started_at,
                        finished_at=time.time(),
                        attempts=attempts[node_id],
                        cache_hit=False,
                        error=error_msg,
                    )
                )
                if self.retry_policy.timeout_s is not None:
                    raise SchedulerTimeoutError(error_msg) from exc
                raise SchedulerRetryError(error_msg) from exc

            finished_at = time.time()
            if getattr(node.stage, "cfg", None) is not None:
                result.provenance.setdefault("cfg_hash", hash_model(node.stage.cfg))
            if policy_hash is not None:
                result.provenance.setdefault("policy_hash", policy_hash)
            result.provenance.setdefault("version", node.version or "v2")
            result.provenance.setdefault("wall_time_s", finished_at - started_at)

            acc.consume(node.id, result)
            results[node_id] = result
            if self.cache is not None:
                self.cache.put(payload["cache_key"], result)
            if self.model_packager is not None and node.metadata.get("model_artifact"):
                package = self.model_packager.package(node_id, result)
                acc.provenance.setdefault("model_packages", []).append(
                    {"node_id": node_id, "path": str(package.path)}
                )

            provenance_records.append(
                NodeProvenance(
                    node_id=node_id,
                    started_at=started_at,
                    finished_at=finished_at,
                    attempts=attempts[node_id],
                )
            )
            execution_order.append(node_id)

            for dependent in dag.reverse_deps[node_id]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    ready.append(dependent)

        self.scheduler.shutdown()
        acc.provenance["node_runs"] = [asdict(record) for record in provenance_records]
        return DagRunResult(
            results=results,
            metrics=acc.metrics,
            artifacts=acc.artifacts,
            provenance=acc.provenance,
            execution_order=execution_order,
        )
