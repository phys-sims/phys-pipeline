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
