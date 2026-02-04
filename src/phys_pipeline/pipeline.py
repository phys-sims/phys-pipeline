from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from .accumulator import RunAccumulator
from .hashing import hash_model, hash_policy
from .policy import PolicyBag, PolicyLike, as_policy
from .record import ArtifactRecorder
from .types import PipelineStage, StageConfig, StageResult, State

S = TypeVar("S", bound=State)


class SequentialPipeline(Generic[S]):
    """Validate and execute stages in order.

    This is the default runtime for phys-pipeline. It runs each stage
    sequentially, aggregates metrics/artifacts/provenance via the accumulator,
    and returns a final ``StageResult`` with the last state and all emissions.

    Example:
        pipeline = SequentialPipeline([MyStage(MyConfig())], name="demo")
        result = pipeline.run(SimpleState(payload=1))
    """

    def __init__(
        self,
        stages: Sequence[PipelineStage[S, Any]],
        name: str | None = None,
        *,
        policy: PolicyLike | None = None,
    ):
        self.stages = list(stages)
        self.name = name or ""
        self.policy = as_policy(policy)

    def set_policy(self, policy: PolicyLike | None) -> None:
        self.policy = as_policy(policy)

    def run(
        self,
        state: S,
        *,
        record_artifacts: bool = False,
        recorder: ArtifactRecorder | None = None,
        policy: PolicyLike | None = None,
    ) -> StageResult[S]:
        """Run the pipeline and return the final ``StageResult``.

        Args:
            state: Initial state passed to the first stage.
            record_artifacts: Enable artifact recording via an ``ArtifactRecorder``.
            recorder: Recorder instance used when ``record_artifacts`` is True.
            policy: Optional run-wide overrides passed into each stage.

        Returns:
            ``StageResult`` containing the final state, aggregated metrics,
            artifacts (if recorded), and provenance.
        """
        run_policy = as_policy(policy) if policy is not None else self.policy
        policy_hash = hash_policy(run_policy) if run_policy is not None else None
        res: StageResult[S] = StageResult(state=state)
        acc = RunAccumulator(
            record_artifacts=record_artifacts,
            recorder=recorder,
            ns_stack=[self.name] if self.name else [],
        )
        if policy_hash is not None:
            acc.provenance["policy_hash"] = policy_hash
        for s in self.stages:
            t0 = time.perf_counter()
            out: StageResult[S] = s.process(res.state, policy=run_policy)
            dt = time.perf_counter() - t0

            # Provenance: cfg hash, version, timing
            prov = out.provenance or {}
            if getattr(s, "cfg", None) is not None:
                try:
                    prov.setdefault("cfg_hash", hash_model(s.cfg))
                except Exception:
                    pass
            if policy_hash is not None:
                prov.setdefault("policy_hash", policy_hash)
            prov.setdefault("version", getattr(s, "version", "v1"))
            prov.setdefault("wall_time_s", dt)
            out.provenance = prov

            stage_label = (
                getattr(s, "name", None)
                or (getattr(s, "cfg", None) and getattr(s.cfg, "name", None))
                or s.__class__.__name__
            )
            acc.consume(stage_label, out)
            res.state = out.state

        # Final emission snapshot on the result
        res.metrics = acc.metrics
        res.artifacts = acc.artifacts
        res.provenance = acc.provenance
        return res


@dataclass
class PipelineStageWrapper(PipelineStage[S, StageConfig], Generic[S]):
    """Wrap a sub-pipeline so it behaves like a stage (pipeline-as-stage).

    This is a composition helper for nested pipelines without requiring DAG
    scheduling. The wrapped pipeline is executed whenever the wrapper stage
    is processed.
    """

    pipeline: SequentialPipeline[S]

    def __init__(self, name: str, pipeline: SequentialPipeline[S]):
        super().__init__(StageConfig(name=name))
        self.name = name
        self.pipeline = pipeline

    def process(self, state: S, *, policy: PolicyBag | None = None) -> StageResult[S]:
        return self.pipeline.run(state, policy=policy)
