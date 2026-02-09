from __future__ import annotations

from phys_pipeline.sweep import SweepSpec, expand_sweep
from phys_pipeline.types import NodeSpec, PipelineStage, SimpleState, StageConfig, StageResult


class ScaleConfig(StageConfig):
    scale: float = 1.0


class ScaleStage(PipelineStage[SimpleState, ScaleConfig]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult[SimpleState]:
        new_state = state.deepcopy()
        new_state.payload *= self.cfg.scale
        return StageResult(state=new_state)


def test_expand_sweep_creates_nodes():
    base = NodeSpec(id="scale", stage=ScaleStage(ScaleConfig(scale=1.0)))
    expanded = expand_sweep(
        [base],
        [SweepSpec(node_id="scale", param_grid={"scale": [1.0, 2.0]})],
    )
    ids = {node.id for node in expanded}
    assert "scale__scale-1.0" in ids
    assert "scale__scale-2.0" in ids
