from __future__ import annotations

import io
import json
from pathlib import Path
from types import ModuleType, TracebackType
from typing import Any, Protocol, cast

import numpy as np
from pydantic import BaseModel, Field, model_validator

try:
    import fcntl as _fcntl
except ImportError:  # pragma: no cover - Windows fallback
    _fcntl = None  # type: ignore[assignment]

fcntl: ModuleType | None = cast(ModuleType | None, _fcntl)


class CacheBackend(Protocol):
    name: str

    def get(self, key: str) -> dict[str, Any] | None: ...

    def put(
        self,
        key: str,
        meta: dict[str, Any],
        arrays: dict[str, np.ndarray],
        *,
        ttl_s: int | None = None,
    ) -> None: ...

    def exists(self, key: str) -> bool: ...


class CacheConfig(BaseModel):
    model_config = {"extra": "forbid", "frozen": True}

    backend: str = Field(default="disk", description="disk|shared-disk|redis")
    disk_root: Path = Field(default=Path(".phys_pipeline_cache"))
    shared_lock_suffix: str = ".lock"
    redis_url: str | None = None
    redis_prefix: str = "phys-pipeline"
    redis_ttl_s: int | None = None

    @model_validator(mode="after")
    def _validate_backend(self) -> CacheConfig:
        if self.backend not in {"disk", "shared-disk", "redis"}:
            raise ValueError(f"Unsupported cache backend: {self.backend}")
        if self.backend == "redis" and not self.redis_url:
            raise ValueError("redis_url must be set when backend='redis'")
        return self


def serialize_cache_entry(
    meta: dict[str, Any], arrays: dict[str, np.ndarray]
) -> tuple[bytes, bytes]:
    meta_payload = json.dumps(meta, sort_keys=True, default=str).encode()
    arrays_buffer = io.BytesIO()
    np.savez_compressed(arrays_buffer, **arrays)  # type: ignore[arg-type]
    return meta_payload, arrays_buffer.getvalue()


def deserialize_cache_entry(meta_payload: bytes, arrays_payload: bytes) -> dict[str, Any]:
    meta = json.loads(meta_payload.decode())
    arrays_buffer = io.BytesIO(arrays_payload)
    arrz = np.load(arrays_buffer)
    arrays = {k: arrz[k] for k in arrz.files}
    return {"meta": meta, "arrays": arrays}


class DiskCache:
    name = "disk"

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _paths(self, key: str) -> tuple[Path, Path]:
        return self.root / f"{key}.json", self.root / f"{key}.npz"

    def get(self, key: str) -> dict[str, Any] | None:
        m, d = self._paths(key)
        if not (m.exists() and d.exists()):
            return None
        meta_payload = m.read_bytes()
        arrays_payload = d.read_bytes()
        return deserialize_cache_entry(meta_payload, arrays_payload)

    def put(
        self,
        key: str,
        meta: dict[str, Any],
        arrays: dict[str, np.ndarray],
        *,
        ttl_s: int | None = None,
    ) -> None:
        meta_payload, arrays_payload = serialize_cache_entry(meta, arrays)
        m, d = self._paths(key)
        m.write_bytes(meta_payload)
        d.write_bytes(arrays_payload)

    def exists(self, key: str) -> bool:
        m, d = self._paths(key)
        return m.exists() and d.exists()


class _FileLock:
    def __init__(self, path: Path):
        self.path = path
        self._fh: io.BufferedWriter | None = None

    def __enter__(self) -> _FileLock:
        if fcntl is None:
            return self
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("wb")
        fcntl.flock(self._fh, fcntl.LOCK_EX)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if fcntl is None:
            return
        if self._fh is not None:
            fcntl.flock(self._fh, fcntl.LOCK_UN)
            self._fh.close()


class SharedDiskCache(DiskCache):
    name = "shared-disk"

    def __init__(self, root: Path, *, lock_suffix: str = ".lock"):
        super().__init__(root)
        self.lock_suffix = lock_suffix

    def _lock_path(self, key: str) -> Path:
        return self.root / f"{key}{self.lock_suffix}"

    def get(self, key: str) -> dict[str, Any] | None:
        with _FileLock(self._lock_path(key)):
            return super().get(key)

    def put(
        self,
        key: str,
        meta: dict[str, Any],
        arrays: dict[str, np.ndarray],
        *,
        ttl_s: int | None = None,
    ) -> None:
        with _FileLock(self._lock_path(key)):
            super().put(key, meta, arrays, ttl_s=ttl_s)

    def exists(self, key: str) -> bool:
        with _FileLock(self._lock_path(key)):
            return super().exists(key)


def build_cache_backend(config: CacheConfig) -> CacheBackend:
    if config.backend == "disk":
        return DiskCache(config.disk_root)
    if config.backend == "shared-disk":
        return SharedDiskCache(config.disk_root, lock_suffix=config.shared_lock_suffix)
    from .cache_redis import RedisCache

    return RedisCache(
        config.redis_url or "",
        prefix=config.redis_prefix,
        ttl_s=config.redis_ttl_s,
    )
