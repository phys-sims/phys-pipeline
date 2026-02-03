from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from phys_pipeline.pipeline import SequentialPipeline
from phys_pipeline.record import ArtifactRecorder
from phys_pipeline.types import PipelineStage, SimpleState, StageConfig, StageResult


@dataclass
class DummyFigure:
    saved: list[str]

    def savefig(self, path, **kwargs):  # type: ignore[no-untyped-def]
        with open(path, "wb") as handle:
            handle.write(b"fake-image")
        self.saved.append(str(path))


class ArtifactStage(PipelineStage[SimpleState, StageConfig]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult:  # type: ignore[override]
        fig = DummyFigure(saved=[])

        def _make():
            return fig

        st = state.deepcopy()
        return StageResult(
            state=st,
            artifacts={
                "plot": _make,
                "payload": np.arange(4096),
            },
        )


@pytest.mark.fast
def test_artifacts_recorded_when_enabled(tmp_path):
    recorder = ArtifactRecorder(tmp_path)
    pipe = SequentialPipeline([ArtifactStage(StageConfig(name="artifact"))], name="demo")
    out = pipe.run(SimpleState(payload=None), record_artifacts=True, recorder=recorder)

    assert "demo.artifact.plot" in out.artifacts
    assert out.artifacts["demo.artifact.plot"]["figure"].endswith(".png")
    assert (tmp_path / "demo_artifact_plot.png").exists()


@pytest.mark.fast
def test_artifacts_previewed_when_not_recording():
    pipe = SequentialPipeline([ArtifactStage(StageConfig(name="artifact"))], name="demo")
    out = pipe.run(SimpleState(payload=None))

    assert out.artifacts["demo.artifact.payload"]["shape"] == [4096]


@pytest.mark.fast
def test_artifact_recorder_rejects_non_figure(tmp_path):
    recorder = ArtifactRecorder(tmp_path)

    def _bad():
        return object()

    with pytest.raises(TypeError, match="Figure or Axes-like"):
        recorder.record_figure("bad", _bad)
