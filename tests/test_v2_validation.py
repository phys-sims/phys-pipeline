from __future__ import annotations

import pytest

from phys_pipeline.dag import build_dag
from phys_pipeline.errors import (
    DagCycleError,
    DagDuplicateNodeError,
    DagMissingDependencyError,
)
from phys_pipeline.executor import DagExecutor
from phys_pipeline.policy import PolicyBag
from phys_pipeline.scheduler import LocalScheduler
from phys_pipeline.sweep import SweepSpec, expand_sweep
from phys_pipeline.types import NodeSpec, PipelineStage, SimpleState, StageConfig, StageResult


class AddConfig(StageConfig):
    amount: int = 1


class AddStage(PipelineStage[SimpleState, AddConfig]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult[SimpleState]:
        new_state = state.deepcopy()
        new_state.payload += self.cfg.amount
        return StageResult(state=new_state)


def test_build_dag_rejects_duplicate_nodes():
    nodes = [NodeSpec(id="a"), NodeSpec(id="a")]
    with pytest.raises(DagDuplicateNodeError):
        build_dag(nodes)


def test_build_dag_rejects_missing_dependency():
    nodes = [NodeSpec(id="a", deps=["missing"])]
    with pytest.raises(DagMissingDependencyError):
        build_dag(nodes)


def test_build_dag_rejects_cycle():
    nodes = [NodeSpec(id="a", deps=["b"]), NodeSpec(id="b", deps=["a"])]
    with pytest.raises(DagCycleError):
        build_dag(nodes)


def test_expand_sweep_clones_nodes_with_metadata():
    nodes = [NodeSpec(id="train", stage=AddStage(AddConfig(amount=1)))]
    sweep_specs = [SweepSpec(node_id="train", param_grid={"amount": [1, 3]})]

    expanded = expand_sweep(nodes, sweep_specs)
    expanded_ids = {node.id for node in expanded}

    assert expanded_ids == {"train__amount-1", "train__amount-3"}
    for node in expanded:
        assert node.metadata["sweep"]
        assert node.stage is not None
        assert node.stage.cfg.amount in {1, 3}


def test_dag_executor_records_v2_provenance_and_policy_hash():
    nodes = [NodeSpec(id="a", stage=AddStage(AddConfig(amount=2)))]
    executor = DagExecutor(scheduler=LocalScheduler(max_workers=1, max_cpu=1))
    policy = PolicyBag({"sampling.N": 4})

    result = executor.run(SimpleState(payload=1), nodes, policy=policy)

    node_result = result.results["a"]
    assert node_result.provenance["version"] == "v2"
    assert "policy_hash" in node_result.provenance
    assert result.provenance["policy_hash"] == node_result.provenance["policy_hash"]
