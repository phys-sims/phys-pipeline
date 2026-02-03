from __future__ import annotations

import numpy as np
import pytest

from phys_pipeline.errors import StageContractError
from phys_pipeline.pipeline import SequentialPipeline
from phys_pipeline.types import PipelineStage, SimpleState, StageConfig, StageResult


class BadMetricStage(PipelineStage[SimpleState, StageConfig]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult:  # type: ignore[override]
        st = state.deepcopy()
        return StageResult(state=st, metrics={"oops": np.array([1.0, 2.0])})


@pytest.mark.fast
def test_metrics_must_be_scalar():
    pipe = SequentialPipeline([BadMetricStage(StageConfig(name="bad"))], name="demo")

    with pytest.raises(StageContractError, match="must be a scalar"):
        pipe.run(SimpleState(payload=None))
