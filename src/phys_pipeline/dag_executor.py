from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from .accumulator import RunAccumulator
from .dag import PipelineGraph
from .errors import DAGInputError
from .hashing import (
    DAG_CACHE_VERSION,
    hash_dag_node_cache_key,
    hash_dependency_results,
    hash_model,
    hash_policy,
    hash_stage_result,
    hash_state,
)
from .policy import PolicyLike, as_policy
from .types import StageResult, State

S = TypeVar("S", bound=State)


@dataclass(slots=True)
class DagExecutionResult(Generic[S]):
    results_by_id: dict[str, StageResult[S]]
    metrics: dict[str, float]
    artifacts: dict[str, Any]
    provenance: dict[str, Any]


class DagExecutor(Generic[S]):
    """Single-threaded DAG executor honoring topological order."""

    def run(
        self,
        graph: PipelineGraph[S],
        initial_state: S,
        *,
        policy: PolicyLike | None = None,
        record_artifacts: bool = False,
    ) -> DagExecutionResult[S]:
        run_policy = as_policy(policy)
        policy_hash = hash_policy(run_policy) if run_policy is not None else None
        results_by_id: dict[str, StageResult[S]] = {}
        acc = RunAccumulator(
            record_artifacts=record_artifacts,
            ns_stack=[graph.name] if graph.name else [],
        )
        provenance: dict[str, Any] = {
            "cache_version": DAG_CACHE_VERSION,
            "execution_order": [],
            "nodes": [],
        }
        if policy_hash is not None:
            provenance["policy_hash"] = policy_hash

        for node_id in graph.topo_order:
            node = graph.nodes_by_id[node_id]
            dep_results = {dep: results_by_id[dep] for dep in node.deps}
            if node.deps:
                if node.input_selector is not None:
                    input_state = node.input_selector(dep_results, initial_state)
                elif len(node.deps) == 1:
                    input_state = dep_results[node.deps[0]].state
                else:
                    raise DAGInputError(
                        f"Node '{node_id}' has multiple dependencies but no input selector."
                    )
            else:
                input_state = initial_state

            started_at = time.time()
            t0 = time.perf_counter()
            out = node.stage.process(input_state, policy=run_policy)
            dt = time.perf_counter() - t0
            finished_at = time.time()

            dependency_hashes = hash_dependency_results(dep_results)
            input_state_hash = hash_state(input_state)
            cache_key = hash_dag_node_cache_key(
                node_id=node_id,
                stage=node.stage,
                input_state_hash=input_state_hash,
                dependency_hashes=dependency_hashes,
                policy_hash=policy_hash,
                version=node.version or getattr(node.stage, "version", "v1"),
            )

            node_prov = out.provenance or {}
            if getattr(node.stage, "cfg", None) is not None:
                try:
                    node_prov.setdefault("cfg_hash", hash_model(node.stage.cfg))
                except Exception:
                    pass
            if policy_hash is not None:
                node_prov.setdefault("policy_hash", policy_hash)
            node_prov.update(
                {
                    "node_id": node_id,
                    "deps": list(node.deps),
                    "version": node.version or getattr(node.stage, "version", "v1"),
                    "wall_time_s": dt,
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "input_state_hash": input_state_hash,
                    "dependency_hashes": dependency_hashes,
                    "cache_key": cache_key,
                    "output_hash": hash_stage_result(out),
                }
            )
            out.provenance = node_prov

            acc.consume(node.label(), out)
            results_by_id[node_id] = out
            provenance["execution_order"].append(node_id)
            provenance["nodes"].append(node_prov)

        return DagExecutionResult(
            results_by_id=results_by_id,
            metrics=acc.metrics,
            artifacts=acc.artifacts,
            provenance=provenance,
        )
