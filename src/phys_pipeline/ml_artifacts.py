from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .types import StageResult


@dataclass(slots=True)
class ModelArtifactPackage:
    path: Path
    metadata: dict[str, Any]


class ModelArtifactPackager:
    """Package ML artifacts for training stages."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def package(self, node_id: str, result: StageResult[Any]) -> ModelArtifactPackage:
        meta = {
            "node_id": node_id,
            "metrics": result.metrics,
            "provenance": result.provenance,
        }
        path = self.root / f"{node_id}_model.json"
        path.write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")
        return ModelArtifactPackage(path=path, metadata=meta)
