from __future__ import annotations

from typing import Iterable, Protocol

from .types import Dag


class Scheduler(Protocol):
    """Scheduler interface for DAG execution."""

    def schedule(self, dag: Dag) -> Iterable[str]:
        """Return an ordered iterable of runnable node IDs."""


class TopoScheduler:
    """Scheduler that returns the DAG's topological order."""

    def schedule(self, dag: Dag) -> Iterable[str]:
        return dag.topo_order()
