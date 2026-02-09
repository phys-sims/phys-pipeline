from __future__ import annotations

import time

import pytest

from phys_pipeline.executor import DagExecutor, RetryPolicy
from phys_pipeline.scheduler import LocalScheduler
from phys_pipeline.types import (
    DagState,
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
        return StageResult(state=new_state, metrics={"amount": float(self.cfg.amount)})


class MergeStage(PipelineStage[DagState, StageConfig]):
    def process(self, state: DagState, *, policy=None) -> StageResult[SimpleState]:
        total = sum(s.payload for s in state.inputs.values())
        return StageResult(state=SimpleState(payload=total))


class FailOnceStage(PipelineStage[SimpleState, StageConfig]):
    def __init__(self, cfg: StageConfig):
        super().__init__(cfg)
        self.calls = 0

    def process(self, state: SimpleState, *, policy=None) -> StageResult[SimpleState]:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("boom")
        return StageResult(state=state)


def test_dag_executor_order_and_merge(tmp_path):
    nodes = [
        NodeSpec(id="a", stage=AddStage(AddConfig(amount=1))),
        NodeSpec(id="b", deps=["a"], stage=AddStage(AddConfig(amount=2))),
        NodeSpec(id="c", deps=["a"], stage=AddStage(AddConfig(amount=3))),
        NodeSpec(id="d", deps=["b", "c"], stage=MergeStage(StageConfig())),
    ]
    executor = DagExecutor(scheduler=LocalScheduler(max_workers=2, max_cpu=2))
    result = executor.run(SimpleState(payload=0), nodes)

    assert result.results["d"].state.payload == 7
    assert set(result.execution_order) == {"a", "b", "c", "d"}
    assert "node_runs" in result.provenance


def test_dag_executor_retry_policy():
    nodes = [NodeSpec(id="a", stage=FailOnceStage(StageConfig()))]
    executor = DagExecutor(
        scheduler=LocalScheduler(max_workers=1, max_cpu=1),
        retry_policy=RetryPolicy(max_retries=1, backoff_s=0.0),
    )
    result = executor.run(SimpleState(payload=1), nodes)
    assert result.results["a"].state.payload == 1


def test_dag_executor_timeout_policy():
    class SleepStage(PipelineStage[SimpleState, StageConfig]):
        def process(self, state: SimpleState, *, policy=None) -> StageResult[SimpleState]:
            time.sleep(0.05)
            return StageResult(state=state)

    nodes = [NodeSpec(id="a", stage=SleepStage(StageConfig()))]
    executor = DagExecutor(
        scheduler=LocalScheduler(max_workers=1, max_cpu=1),
        retry_policy=RetryPolicy(max_retries=0, timeout_s=0.001),
    )
    with pytest.raises(Exception):
        executor.run(SimpleState(payload=1), nodes)


def test_dag_executor_mpi_runner():
    class MockRunner:
        def __init__(self):
            self.calls = 0

        def run(self, stage, state, *, resources):
            self.calls += 1
            return stage.process(state)

    runner = MockRunner()
    nodes = [
        NodeSpec(
            id="a",
            stage=AddStage(AddConfig(amount=1)),
            resources=NodeResources(mpi_ranks=2),
        )
    ]
    executor = DagExecutor(
        scheduler=LocalScheduler(max_workers=1, max_cpu=1),
        mpi_runner=runner,
    )
    result = executor.run(SimpleState(payload=0), nodes)
    assert result.results["a"].state.payload == 1
    assert runner.calls == 1
