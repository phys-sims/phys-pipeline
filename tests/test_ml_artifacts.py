from __future__ import annotations

from phys_pipeline.executor import DagExecutor
from phys_pipeline.ml_artifacts import ModelArtifactPackager
from phys_pipeline.scheduler import LocalScheduler
from phys_pipeline.types import NodeSpec, PipelineStage, SimpleState, StageConfig, StageResult


class DummyConfig(StageConfig):
    pass


class DummyStage(PipelineStage[SimpleState, DummyConfig]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult[SimpleState]:
        return StageResult(state=state, metrics={"loss": 0.1})


def test_model_artifact_packaging(tmp_path):
    packager = ModelArtifactPackager(tmp_path)
    nodes = [
        NodeSpec(
            id="train",
            stage=DummyStage(DummyConfig()),
            metadata={"model_artifact": True},
        )
    ]
    executor = DagExecutor(
        scheduler=LocalScheduler(max_workers=1, max_cpu=1),
        model_packager=packager,
    )
    result = executor.run(SimpleState(payload=1), nodes)
    packages = result.provenance.get("model_packages", [])
    assert packages
