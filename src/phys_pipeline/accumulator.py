from __future__ import annotations

from typing import Any

import numpy as np

from .errors import StageContractError
from .types import StageResult


def _is_small(x: Any) -> bool:
    if isinstance(x, (str, int, float, dict)):
        return True
    if isinstance(x, np.ndarray):
        return x.size <= 2048
    return False


def _preview(x: Any) -> Any:
    if isinstance(x, np.ndarray):
        n = min(16, x.size)
        return {
            "dtype": str(x.dtype),
            "shape": list(x.shape),
            "head": x.ravel()[:n].tolist(),
        }
    return str(type(x))


def _to_scalar(v: Any, key: str, stage_name: str) -> float:
    if isinstance(v, (int, float)):
        return float(v)
    if hasattr(v, "item") and not isinstance(v, np.ndarray):
        return float(v.item())
    raise StageContractError(
        f"metrics['{key}'] from stage '{stage_name}' must be a scalar; "
        "put arrays into state.meta or artifacts."
    )


class RunAccumulator:
    """Merges per-stage emissions; supports nested namespaces."""

    def __init__(
        self,
        record_artifacts: bool = False,
        recorder: Any | None = None,
        ns_stack: list[str] | None = None,
    ):
        self.metrics: dict[str, float] = {}
        self.artifacts: dict[str, Any] = {}
        self.provenance: dict[str, Any] = {"stages": []}
        self._record_artifacts = record_artifacts
        self._recorder = recorder
        self._ns = ns_stack or []

    def _nskey(self, k: str, stage_name: str) -> str:
        prefix = ".".join(self._ns + [stage_name]) if stage_name else ".".join(self._ns)
        return f"{prefix}.{k}" if prefix else k

    def consume(self, stage_name: str, res: StageResult) -> None:
        for k, v in (res.metrics or {}).items():
            self.metrics[self._nskey(k, stage_name)] = _to_scalar(v, k, stage_name)
        for k, v in (res.artifacts or {}).items():
            key = self._nskey(k, stage_name)
            if self._record_artifacts and self._recorder is not None:
                if callable(v):
                    path = self._recorder.record_figure(key, v)
                    self.artifacts[key] = {"figure": path}
                else:
                    self.artifacts[key] = {"preview": _preview(v)}
            else:
                self.artifacts[key] = v if _is_small(v) else _preview(v)
        if res.provenance:
            self.provenance["stages"].append(res.provenance | {"stage": stage_name})
