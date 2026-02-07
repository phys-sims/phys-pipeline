from __future__ import annotations

from typing import Any

import numpy as np

from .cache import CacheBackend, deserialize_cache_entry, serialize_cache_entry


class RedisCache(CacheBackend):
    name = "redis"

    def __init__(self, url: str, *, prefix: str = "phys-pipeline", ttl_s: int | None = None):
        try:
            import redis  # type: ignore[import-not-found]
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Redis backend requires the 'redis' package. Install via 'pip install redis'."
            ) from exc
        self._redis = redis.Redis.from_url(url)
        self.prefix = prefix
        self.ttl_s = ttl_s

    def _keys(self, key: str) -> tuple[str, str]:
        base = f"{self.prefix}:{key}"
        return f"{base}:meta", f"{base}:arrays"

    def get(self, key: str) -> dict[str, Any] | None:
        meta_key, arrays_key = self._keys(key)
        meta_payload, arrays_payload = self._redis.mget([meta_key, arrays_key])
        if meta_payload is None or arrays_payload is None:
            return None
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
        meta_key, arrays_key = self._keys(key)
        pipeline = self._redis.pipeline()
        pipeline.set(meta_key, meta_payload)
        pipeline.set(arrays_key, arrays_payload)
        effective_ttl = ttl_s if ttl_s is not None else self.ttl_s
        if effective_ttl:
            pipeline.expire(meta_key, effective_ttl)
            pipeline.expire(arrays_key, effective_ttl)
        pipeline.execute()

    def exists(self, key: str) -> bool:
        meta_key, arrays_key = self._keys(key)
        return bool(self._redis.exists(meta_key, arrays_key) == 2)
