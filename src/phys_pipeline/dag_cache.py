from __future__ import annotations

import base64
import pickle
from dataclasses import dataclass
from typing import Any

from .cache import CacheBackend
from .types import StageResult, State


@dataclass(slots=True)
class DagCacheEntry:
    state: State
    metrics: dict[str, float]
    provenance: dict[str, Any]


class DagCache:
    """Cache wrapper for DAG node results."""

    def __init__(self, backend: CacheBackend):
        self.backend = backend

    def get(self, key: str) -> DagCacheEntry | None:
        payload = self.backend.get(key)
        if payload is None:
            return None
        meta = payload["meta"]
        state_blob = meta.get("state_blob")
        if state_blob is None:
            return None
        state = pickle.loads(base64.b64decode(state_blob))
        return DagCacheEntry(
            state=state,
            metrics=meta.get("metrics", {}),
            provenance=meta.get("provenance", {}),
        )

    def put(self, key: str, result: StageResult[State]) -> None:
        state_blob = base64.b64encode(pickle.dumps(result.state)).decode()
        meta = {
            "state_blob": state_blob,
            "metrics": result.metrics,
            "provenance": result.provenance,
        }
        self.backend.put(key, meta=meta, arrays={})
