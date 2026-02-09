from __future__ import annotations

import time
from pathlib import Path

from phys_pipeline.cache import DiskCache
from phys_pipeline.dag_cache import DagCache
from phys_pipeline.executor import DagExecutor
from phys_pipeline.scheduler import LocalScheduler
from phys_pipeline.types import (
    NodeResources,
    NodeSpec,
    PipelineStage,
    SimpleState,
    StageConfig,
    StageResult,
)


class AddConfig(StageConfig):
    amount: int = 1


class AddStage(PipelineStage[SimpleState, AddConfig]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult[SimpleState]:
        new_state = state.deepcopy()
        new_state.payload += self.cfg.amount
        return StageResult(state=new_state)


def benchmark_cache(tmp_root: Path) -> None:
    cache_backend = DiskCache(tmp_root)
    cache = DagCache(cache_backend)
    nodes = [NodeSpec(id="a", stage=AddStage(AddConfig(amount=2)))]
    executor = DagExecutor(
        scheduler=LocalScheduler(max_workers=1, max_cpu=1),
        cache=cache,
    )
    start = time.perf_counter()
    executor.run(SimpleState(payload=1), nodes)
    cold = time.perf_counter() - start

    start = time.perf_counter()
    executor.run(SimpleState(payload=1), nodes)
    warm = time.perf_counter() - start
    print(f"Cache benchmark: cold={cold:.4f}s warm={warm:.4f}s")


def benchmark_scheduler() -> None:
    scheduler = LocalScheduler(max_workers=4, max_cpu=4)
    handles = [
        scheduler.submit(f"job{i}", lambda: time.sleep(0.01), resources=NodeResources())
        for i in range(8)
    ]
    start = time.perf_counter()
    while handles:
        handle = scheduler.wait_any(handles)
        handles = [h for h in handles if h.job_id != handle.job_id]
    scheduler.shutdown()
    elapsed = time.perf_counter() - start
    print(f"Scheduler benchmark: {elapsed:.4f}s")


if __name__ == "__main__":
    root = Path(".benchmarks")
    root.mkdir(exist_ok=True)
    benchmark_cache(root)
    benchmark_scheduler()
