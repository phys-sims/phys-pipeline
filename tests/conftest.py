# conftest.py  (project root)
from pathlib import Path

import pytest

from phys_pipeline.record import ArtifactRecorder


def pytest_addoption(parser):
    g = parser.getgroup("phys-artifacts")
    g.addoption("--save-artifacts", action="store_true", help="Write figures/blobs from stages")
    g.addoption("--artdir", default="artifacts", help="Artifacts output dir")


@pytest.fixture(scope="session")
def artifact_recorder(request):
    if not request.config.getoption("--save-artifacts"):
        return None
    root = Path(request.config.getoption("--artdir"))
    root.mkdir(parents=True, exist_ok=True)
    print(f"\n[artifacts] saving to: {root.resolve()}")
    return ArtifactRecorder(root)


@pytest.fixture
def run_pipeline(artifact_recorder):
    def _run(pipe, state):
        return pipe.run(
            state,
            record_artifacts=artifact_recorder is not None,
            recorder=artifact_recorder,
        )

    return _run


# comment to test CI
