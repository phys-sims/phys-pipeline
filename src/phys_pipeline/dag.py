from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .errors import DagCycleError, DagDuplicateNodeError, DagMissingDependencyError
from .types import NodeSpec


@dataclass(frozen=True, slots=True)
class Dag:
    nodes_by_id: dict[str, NodeSpec]
    deps: dict[str, list[str]]
    reverse_deps: dict[str, list[str]]
    topo_order: list[str]


@dataclass(frozen=True, slots=True)
class PipelineGraph:
    nodes: list[NodeSpec]
    dag: Dag

    @classmethod
    def from_nodes(cls, nodes: list[NodeSpec]) -> PipelineGraph:
        return cls(nodes=nodes, dag=build_dag(nodes))


def build_dag(nodes: list[NodeSpec]) -> Dag:
    nodes_by_id: dict[str, NodeSpec] = {}
    deps: dict[str, list[str]] = {}
    reverse_deps: dict[str, list[str]] = {}

    for node in nodes:
        if node.id in nodes_by_id:
            raise DagDuplicateNodeError(f"Duplicate node id: {node.id}")
        nodes_by_id[node.id] = node
        deps[node.id] = list(node.deps)
        reverse_deps[node.id] = []

    for node_id, node_deps in deps.items():
        for dep in node_deps:
            if dep not in nodes_by_id:
                raise DagMissingDependencyError(f"Missing dependency '{dep}' for node '{node_id}'")
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
        raise DagCycleError("Cycle detected in DAG")

    return Dag(
        nodes_by_id=nodes_by_id,
        deps=deps,
        reverse_deps=reverse_deps,
        topo_order=topo_order,
    )
