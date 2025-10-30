from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


class DiskCache:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _paths(self, key: str) -> tuple[Path, Path]:
        return self.root / f"{key}.json", self.root / f"{key}.npz"

    def get(self, key: str) -> dict[str, Any] | None:
        m, d = self._paths(key)
        if not (m.exists() and d.exists()):
            return None
        with m.open("rb") as f:
            meta = json.load(f)
        arrz = np.load(d)
        arrays = {k: arrz[k] for k in arrz.files}
        return {"meta": meta, "arrays": arrays}

    def put(self, key: str, meta: dict, arrays: dict) -> None:
        m, d = self._paths(key)
        with m.open("wb") as f:
            f.write(json.dumps(meta, sort_keys=True, default=str).encode())
        np.savez_compressed(d, **arrays)
