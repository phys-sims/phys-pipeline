from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any

from .types import NodeSpec, PipelineStage, StageConfig


@dataclass(frozen=True, slots=True)
class SweepSpec:
    node_id: str
    param_grid: dict[str, list[Any]]


def _clone_stage(stage: PipelineStage[Any, StageConfig], cfg: StageConfig) -> PipelineStage:
    return stage.__class__(cfg)


def expand_sweep(nodes: list[NodeSpec], sweep_specs: list[SweepSpec]) -> list[NodeSpec]:
    """Expand parameter sweeps into cloned DAG nodes."""
    nodes_by_id = {node.id: node for node in nodes}
    sweep_ids = {s.node_id for s in sweep_specs}
    expanded: list[NodeSpec] = [node for node in nodes if node.id not in sweep_ids]

    for spec in sweep_specs:
        base = nodes_by_id[spec.node_id]
        if base.stage is None:
            raise ValueError(f"Sweep node '{spec.node_id}' has no stage attached.")
        grid_items = sorted(spec.param_grid.items())
        keys = [k for k, _ in grid_items]
        values = [v for _, v in grid_items]
        for combo in itertools.product(*values):
            updates = dict(zip(keys, combo))
            cfg = base.stage.cfg.model_copy(update=updates)
            stage = _clone_stage(base.stage, cfg)
            suffix = "_".join(f"{k}-{v}" for k, v in updates.items())
            node_id = f"{base.id}__{suffix}"
            expanded.append(
                NodeSpec(
                    id=node_id,
                    deps=list(base.deps),
                    op_name=base.op_name,
                    version=base.version,
                    stage=stage,
                    resources=base.resources,
                    metadata={**base.metadata, "sweep": updates},
                )
            )

    return expanded
