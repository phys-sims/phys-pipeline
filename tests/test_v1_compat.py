from __future__ import annotations

from phys_pipeline.pipeline import SequentialPipeline
from phys_pipeline.types import PipelineStage, SimpleState, StageConfig, StageResult


class MultiplyConfig(StageConfig):
    factor: int = 2


class MultiplyStage(PipelineStage[SimpleState, MultiplyConfig]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult[SimpleState]:
        new_state = state.deepcopy()
        new_state.payload *= self.cfg.factor
        return StageResult(state=new_state)


def test_v1_sequential_pipeline_compatibility():
    pipeline = SequentialPipeline([MultiplyStage(MultiplyConfig(factor=3))])
    result = pipeline.run(SimpleState(payload=2))
    assert result.state.payload == 6
