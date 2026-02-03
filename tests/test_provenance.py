from __future__ import annotations

import pytest

from phys_pipeline.hashing import hash_model, hash_policy
from phys_pipeline.pipeline import SequentialPipeline
from phys_pipeline.policy import PolicyBag
from phys_pipeline.types import PipelineStage, SimpleState, StageConfig, StageResult


class OneCfg(StageConfig):
    factor: int = 2


class OneStage(PipelineStage[SimpleState, OneCfg]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult:  # type: ignore[override]
        st = state.deepcopy()
        st.meta["x"] = self.cfg.factor
        return StageResult(state=st)


class TwoCfg(StageConfig):
    offset: int = 3


class TwoStage(PipelineStage[SimpleState, TwoCfg]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult:  # type: ignore[override]
        st = state.deepcopy()
        st.meta["x"] += self.cfg.offset
        return StageResult(state=st)


@pytest.mark.fast
def test_provenance_records_multiple_stages_and_policy_hash():
    st0 = SimpleState(payload=None)
    pipe = SequentialPipeline(
        [
            OneStage(OneCfg(name="one", factor=4)),
            TwoStage(TwoCfg(name="two", offset=5)),
        ],
        name="demo",
    )
    policy = PolicyBag({"sampling.N": 2})
    out = pipe.run(st0, policy=policy)

    assert out.provenance["policy_hash"] == hash_policy(policy)
    assert [p["stage"] for p in out.provenance["stages"]] == ["one", "two"]
    first, second = out.provenance["stages"]
    assert first["cfg_hash"] == hash_model(pipe.stages[0].cfg)
    assert second["cfg_hash"] == hash_model(pipe.stages[1].cfg)
    assert "wall_time_s" in first
    assert "wall_time_s" in second
