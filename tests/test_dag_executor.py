from __future__ import annotations

from typing import Any

import pytest

from phys_pipeline.dag import PipelineNode, build_pipeline_graph
from phys_pipeline.dag_executor import DagExecutor
from phys_pipeline.errors import DAGInputError
from phys_pipeline.types import PipelineStage, SimpleState, StageConfig, StageResult


class AddCfg(StageConfig):
    delta: int = 1


class AddStage(PipelineStage[SimpleState, AddCfg]):
    def process(self, state: SimpleState, *, policy: Any | None = None) -> StageResult:
        st = state.deepcopy()
        st.payload = (st.payload or 0) + self.cfg.delta
        return StageResult(state=st, metrics={"delta": float(self.cfg.delta)})


def test_dag_executor_runs_in_topo_order_and_records_provenance():
    nodes = [
        PipelineNode(id="a", stage=AddStage(AddCfg(name="a", delta=2))),
        PipelineNode(id="b", stage=AddStage(AddCfg(name="b", delta=3)), deps=["a"]),
    ]
    graph = build_pipeline_graph(nodes, name="demo")

    result = DagExecutor().run(graph, SimpleState(payload=1))

    assert result.results_by_id["b"].state.payload == 6
    assert result.provenance["execution_order"] == ["a", "b"]
    assert result.provenance["nodes"][0]["node_id"] == "a"
    assert "cache_key" in result.provenance["nodes"][0]


def test_dag_executor_requires_selector_for_multiple_deps():
    nodes = [
        PipelineNode(id="a", stage=AddStage(AddCfg(name="a", delta=2))),
        PipelineNode(id="b", stage=AddStage(AddCfg(name="b", delta=3))),
        PipelineNode(id="c", stage=AddStage(AddCfg(name="c", delta=1)), deps=["a", "b"]),
    ]
    graph = build_pipeline_graph(nodes)

    with pytest.raises(DAGInputError, match="multiple dependencies"):
        DagExecutor().run(graph, SimpleState(payload=0))


def test_dag_executor_uses_input_selector_for_merge():
    def merge_states(dep_results: dict[str, StageResult], initial: SimpleState) -> SimpleState:
        total = sum(res.state.payload for res in dep_results.values())
        return SimpleState(payload=total)

    nodes = [
        PipelineNode(id="a", stage=AddStage(AddCfg(name="a", delta=2))),
        PipelineNode(id="b", stage=AddStage(AddCfg(name="b", delta=3))),
        PipelineNode(
            id="c",
            stage=AddStage(AddCfg(name="c", delta=1)),
            deps=["a", "b"],
            input_selector=merge_states,
        ),
    ]
    graph = build_pipeline_graph(nodes)

    result = DagExecutor().run(graph, SimpleState(payload=0))

    assert result.results_by_id["c"].state.payload == 6
