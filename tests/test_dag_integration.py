from __future__ import annotations

from phys_pipeline.cache import DiskCache
from phys_pipeline.dag_cache import DagCache
from phys_pipeline.executor import DagExecutor
from phys_pipeline.scheduler import LocalScheduler
from phys_pipeline.types import NodeSpec, PipelineStage, SimpleState, StageConfig, StageResult


class AddConfig(StageConfig):
    amount: int = 1


class AddStage(PipelineStage[SimpleState, AddConfig]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult[SimpleState]:
        new_state = state.deepcopy()
        new_state.payload += self.cfg.amount
        return StageResult(state=new_state)


def test_dag_integration_cache_hit(tmp_path):
    cache_backend = DiskCache(tmp_path)
    cache = DagCache(cache_backend)
    nodes = [NodeSpec(id="a", stage=AddStage(AddConfig(amount=2)))]
    executor = DagExecutor(
        scheduler=LocalScheduler(max_workers=1, max_cpu=1),
        cache=cache,
    )
    first = executor.run(SimpleState(payload=1), nodes)
    executor = DagExecutor(
        scheduler=LocalScheduler(max_workers=1, max_cpu=1),
        cache=cache,
    )
    second = executor.run(SimpleState(payload=1), nodes)
    assert first.results["a"].state.payload == 3
    assert second.results["a"].state.payload == 3
    node_runs = second.provenance.get("node_runs", [])
    assert any(run.get("cache_hit") for run in node_runs)
