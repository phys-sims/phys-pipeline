from __future__ import annotations

from collections import deque
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, TypeVar, cast

from .errors import (
    DAGCycleError,
    DAGDuplicateNodeError,
    DAGMissingDependencyError,
)
from .types import NodeSpec, PipelineStage, StageResult, State


@dataclass(frozen=True, slots=True)
class Dag:
    nodes_by_id: dict[str, NodeSpec]
    deps: dict[str, list[str]]
    reverse_deps: dict[str, list[str]]
    topo_order: list[str]


class NodeLike(Protocol):
    id: str
    deps: list[str]


S = TypeVar("S", bound=State)
InputSelector = Callable[[dict[str, StageResult[S]], S], S]


@dataclass(frozen=True, slots=True)
class PipelineNode(Generic[S]):
    id: str
    stage: PipelineStage[S, Any]
    deps: list[str] = field(default_factory=list)
    op_name: str = ""
    version: str = ""
    input_selector: InputSelector[S] | None = None

    def label(self) -> str:
        return (
            self.op_name
            or getattr(self.stage, "name", None)
            or (getattr(self.stage, "cfg", None) and getattr(self.stage.cfg, "name", None))
            or self.stage.__class__.__name__
        )


@dataclass(frozen=True, slots=True)
class PipelineGraph(Generic[S]):
    name: str
    nodes_by_id: dict[str, PipelineNode[S]]
    dag: Dag

    @property
    def topo_order(self) -> list[str]:
        return list(self.dag.topo_order)

    @property
    def deps(self) -> dict[str, list[str]]:
        return self.dag.deps

    @property
    def reverse_deps(self) -> dict[str, list[str]]:
        return self.dag.reverse_deps


def build_pipeline_graph(nodes: list[PipelineNode[S]], *, name: str = "") -> PipelineGraph[S]:
    dag = build_dag(cast(Sequence[NodeLike], nodes))
    nodes_by_id = {node.id: node for node in nodes}
    return PipelineGraph(name=name, nodes_by_id=nodes_by_id, dag=dag)


def build_dag(nodes: Sequence[NodeLike]) -> Dag:
    nodes_by_id: dict[str, NodeSpec] = {}
    deps: dict[str, list[str]] = {}
    reverse_deps: dict[str, list[str]] = {}

    for node in nodes:
        if node.id in nodes_by_id:
            raise DAGDuplicateNodeError(f"Duplicate node id: {node.id}")
        nodes_by_id[node.id] = NodeSpec(
            id=node.id,
            deps=list(node.deps),
            op_name=getattr(node, "op_name", ""),
            version=getattr(node, "version", ""),
        )
        deps[node.id] = list(node.deps)
        reverse_deps[node.id] = []

    for node_id, node_deps in deps.items():
        for dep in node_deps:
            if dep not in nodes_by_id:
                raise DAGMissingDependencyError(f"Missing dependency '{dep}' for node '{node_id}'")
            reverse_deps[dep].append(node_id)

    in_degree = {node_id: len(node_deps) for node_id, node_deps in deps.items()}
    ready = deque(sorted(node_id for node_id, degree in in_degree.items() if degree == 0))
    topo_order: list[str] = []

    while ready:
        node_id = ready.popleft()
        topo_order.append(node_id)
        for dependent in sorted(reverse_deps[node_id]):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                ready.append(dependent)

    if len(topo_order) != len(nodes_by_id):
        raise DAGCycleError("Cycle detected in DAG")

    return Dag(
        nodes_by_id=nodes_by_id,
        deps=deps,
        reverse_deps=reverse_deps,
        topo_order=topo_order,
    )
