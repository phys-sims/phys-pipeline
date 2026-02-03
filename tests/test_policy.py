import pytest

from phys_pipeline.hashing import hash_policy
from phys_pipeline.pipeline import SequentialPipeline
from phys_pipeline.policy import PolicyBag
from phys_pipeline.types import PipelineStage, SimpleState, StageConfig, StageResult


class PolicyCfg(StageConfig):
    N: int = 4


class PolicyStage(PipelineStage[SimpleState, PolicyCfg]):
    def process(self, state: SimpleState, *, policy: PolicyBag | None = None) -> StageResult:
        n = self.cfg.N
        if policy is not None:
            n = int(policy.get("sampling.N", n))
        st = state.deepcopy()
        st.meta["N"] = n
        return StageResult(state=st)


@pytest.mark.fast
def test_policy_passed_and_hashed():
    st0 = SimpleState(payload=None)
    pipe = SequentialPipeline(
        [PolicyStage(PolicyCfg(name="policy", N=4))],
        name="demo",
    )
    policy = PolicyBag({"sampling.N": 8})
    out = pipe.run(st0, policy=policy)

    assert out.state.meta["N"] == 8
    assert out.provenance["policy_hash"] == hash_policy(policy)
    assert out.provenance["stages"][0]["policy_hash"] == out.provenance["policy_hash"]


@pytest.mark.fast
def test_default_policy_used_when_run_policy_missing():
    st0 = SimpleState(payload=None)
    policy = PolicyBag({"sampling.N": 10})
    pipe = SequentialPipeline(
        [PolicyStage(PolicyCfg(name="policy", N=4))],
        name="demo",
        policy=policy,
    )

    out = pipe.run(st0)

    assert out.state.meta["N"] == 10
    assert out.provenance["policy_hash"] == hash_policy(policy)
    assert out.provenance["stages"][0]["policy_hash"] == out.provenance["policy_hash"]


@pytest.mark.fast
def test_run_policy_overrides_default_policy():
    st0 = SimpleState(payload=None)
    default_policy = PolicyBag({"sampling.N": 10})
    run_policy = PolicyBag({"sampling.N": 6})
    pipe = SequentialPipeline(
        [PolicyStage(PolicyCfg(name="policy", N=4))],
        name="demo",
        policy=default_policy,
    )

    out = pipe.run(st0, policy=run_policy)

    assert out.state.meta["N"] == 6
    assert out.provenance["policy_hash"] == hash_policy(run_policy)
    assert out.provenance["policy_hash"] != hash_policy(default_policy)
