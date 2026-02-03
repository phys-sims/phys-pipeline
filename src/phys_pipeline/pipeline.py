from __future__ import annotations

import time
from dataclasses import dataclass

from .accumulator import RunAccumulator
from .hashing import hash_model, hash_policy
from .policy import PolicyBag, PolicyLike, as_policy
from .record import ArtifactRecorder
from .types import PipelineStage, StageConfig, StageResult, State


class SequentialPipeline:
    """Validates and executes stages in order; merges emissions via accumulator."""

    def __init__(
        self,
        stages: list[PipelineStage],
        name: str | None = None,
        *,
        policy: PolicyLike | None = None,
    ):
        self.stages = stages
        self.name = name or ""
        self.policy = as_policy(policy)

    def set_policy(self, policy: PolicyLike | None) -> None:
        self.policy = as_policy(policy)

    def run(
        self,
        state: State,
        *,
        record_artifacts: bool = False,
        recorder: ArtifactRecorder | None = None,
        policy: PolicyLike | None = None,
    ) -> StageResult:
        run_policy = as_policy(policy) if policy is not None else self.policy
        policy_hash = hash_policy(run_policy) if run_policy is not None else None
        res = StageResult(state=state)
        acc = RunAccumulator(
            record_artifacts=record_artifacts,
            recorder=recorder,
            ns_stack=[self.name] if self.name else [],
        )
        if policy_hash is not None:
            acc.provenance["policy_hash"] = policy_hash
        for s in self.stages:
            t0 = time.perf_counter()
            out: StageResult = s.process(res.state, policy=run_policy)
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
class PipelineStageWrapper(PipelineStage[State, StageConfig]):
    """Wrap a sub-pipeline so it behaves like a stage (pipeline-as-stage)."""

    pipeline: SequentialPipeline

    def __init__(self, name: str, pipeline: SequentialPipeline):
        self.name = name
        self.pipeline = pipeline

    def process(self, state: State, *, policy: PolicyBag | None = None) -> StageResult:
        return self.pipeline.run(state, policy=policy)
