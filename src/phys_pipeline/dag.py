from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .errors import PipelineError
from .types import NodeSpec


@dataclass(frozen=True, slots=True)
class Dag:
    nodes_by_id: dict[str, NodeSpec]
    deps: dict[str, list[str]]
    reverse_deps: dict[str, list[str]]
    topo_order: list[str]


def build_dag(nodes: list[NodeSpec]) -> Dag:
    nodes_by_id: dict[str, NodeSpec] = {}
    deps: dict[str, list[str]] = {}
    reverse_deps: dict[str, list[str]] = {}

    for node in nodes:
        if node.id in nodes_by_id:
            raise PipelineError(f"Duplicate node id: {node.id}")
        nodes_by_id[node.id] = node
        deps[node.id] = list(node.deps)
        reverse_deps[node.id] = []

    for node_id, node_deps in deps.items():
        for dep in node_deps:
            if dep not in nodes_by_id:
                raise PipelineError(f"Missing dependency '{dep}' for node '{node_id}'")
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
        raise PipelineError("Cycle detected in DAG")

    return Dag(
        nodes_by_id=nodes_by_id,
        deps=deps,
        reverse_deps=reverse_deps,
        topo_order=topo_order,
    )
