from __future__ import annotations

import importlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, TypeGuard


@dataclass
class JSONLRecorder:
    path: Path

    def write(self, row: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


class FigureLike(Protocol):
    def savefig(self, *args: Any, **kwargs: Any) -> Any: ...


class AxesLike(Protocol):
    @property
    def figure(self) -> FigureLike: ...


def is_figure(x: FigureLike | AxesLike) -> TypeGuard[FigureLike]:
    return hasattr(x, "savefig")


def is_axes(x: FigureLike | AxesLike) -> TypeGuard[AxesLike]:
    return hasattr(x, "figure")


class ArtifactRecorder:
    """Lightweight artifact storage (images/npz/blobs)."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str, suffix: str) -> Path:
        safe = key.replace("/", "_").replace(".", "_")
        return self.root / f"{safe}{suffix}"

    def record_blob(self, key: str, data: Any) -> str:
        p = self._path_for(key, ".json")
        with p.open("w", encoding="utf-8") as f:
            f.write(json.dumps(data, default=str))
        return str(p)

    def record_figure(
        self,
        key: str,
        fig_factory: Callable[[], FigureLike | AxesLike],
    ) -> str:
        obj = fig_factory()

        if is_figure(obj):
            fig: FigureLike = obj
        elif is_axes(obj):
            fig = obj.figure
        else:
            raise TypeError("fig_factory must return a Figure or Axes-like object")

        p = self._path_for(key, ".png")
        fig.savefig(p, dpi=120, bbox_inches="tight")

        try:
            plt = importlib.import_module("matplotlib.pyplot")
            getattr(plt, "close", lambda *_: None)(fig)
        except Exception:
            pass

        return str(p)
