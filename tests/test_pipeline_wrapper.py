from phys_pipeline.pipeline import PipelineStageWrapper, SequentialPipeline
from phys_pipeline.policy import PolicyBag
from phys_pipeline.types import PipelineStage, SimpleState, StageConfig, StageResult


class IncrementCfg(StageConfig):
    step: int = 1


class IncrementStage(PipelineStage[SimpleState, IncrementCfg]):
    def process(
        self, state: SimpleState, *, policy: PolicyBag | None = None
    ) -> StageResult[SimpleState]:
        st = state.deepcopy()
        st.payload = (st.payload or 0) + self.cfg.step
        return StageResult(state=st)


def test_pipeline_wrapper_composes_stages() -> None:
    inner = SequentialPipeline(
        [IncrementStage(IncrementCfg(name="inc", step=2))],
        name="inner",
    )
    wrapper = PipelineStageWrapper("inner-wrapper", inner)
    outer = SequentialPipeline(
        [
            wrapper,
            IncrementStage(IncrementCfg(name="inc2", step=3)),
        ],
        name="outer",
    )
    result = outer.run(SimpleState(payload=1))
    assert result.state.payload == 6
