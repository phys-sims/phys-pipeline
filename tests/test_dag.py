from __future__ import annotations

import pytest

from phys_pipeline.dag import build_dag
from phys_pipeline.errors import PipelineError
from phys_pipeline.types import NodeSpec


def test_build_dag_topo_and_adjacency():
    nodes = [
        NodeSpec(id="a", deps=[], op_name="op", version="v1"),
        NodeSpec(id="b", deps=["a"], op_name="op", version="v1"),
        NodeSpec(id="c", deps=["a"], op_name="op", version="v1"),
        NodeSpec(id="d", deps=["b", "c"], op_name="op", version="v1"),
    ]

    dag = build_dag(nodes)

    assert dag.topo_order[0] == "a"
    assert set(dag.topo_order[1:3]) == {"b", "c"}
    assert dag.topo_order[-1] == "d"
    assert dag.deps["d"] == ["b", "c"]
    assert set(dag.reverse_deps["a"]) == {"b", "c"}


def test_build_dag_duplicate_ids():
    nodes = [
        NodeSpec(id="a", deps=[]),
        NodeSpec(id="a", deps=[]),
    ]

    with pytest.raises(PipelineError, match="Duplicate node id"):
        build_dag(nodes)


def test_build_dag_missing_dep():
    nodes = [
        NodeSpec(id="a", deps=["missing"]),
    ]

    with pytest.raises(PipelineError, match="Missing dependency"):
        build_dag(nodes)


def test_build_dag_cycle_detection():
    nodes = [
        NodeSpec(id="a", deps=["b"]),
        NodeSpec(id="b", deps=["a"]),
    ]

    with pytest.raises(PipelineError, match="Cycle detected"):
        build_dag(nodes)
