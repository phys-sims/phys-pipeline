import os

import numpy as np
import pytest

from phys_pipeline.cache import (
    CacheConfig,
    DiskCache,
    build_cache_backend,
    deserialize_cache_entry,
    serialize_cache_entry,
)


def _sample_payload():
    meta = {"stage": "demo", "count": 2}
    arrays = {"x": np.array([1.0, 2.0]), "y": np.arange(3)}
    return meta, arrays


def test_serialize_roundtrip():
    meta, arrays = _sample_payload()
    meta_payload, arrays_payload = serialize_cache_entry(meta, arrays)
    restored = deserialize_cache_entry(meta_payload, arrays_payload)
    assert restored["meta"] == meta
    np.testing.assert_allclose(restored["arrays"]["x"], arrays["x"])
    np.testing.assert_allclose(restored["arrays"]["y"], arrays["y"])


def test_disk_cache_roundtrip(tmp_path):
    meta, arrays = _sample_payload()
    cache = DiskCache(tmp_path)
    cache.put("k1", meta, arrays)
    assert cache.exists("k1")
    restored = cache.get("k1")
    assert restored is not None
    assert restored["meta"] == meta
    np.testing.assert_allclose(restored["arrays"]["x"], arrays["x"])
    np.testing.assert_allclose(restored["arrays"]["y"], arrays["y"])


def test_cache_config_validation():
    with pytest.raises(ValueError, match="Unsupported cache backend"):
        CacheConfig(backend="mem")
    with pytest.raises(ValueError, match="redis_url must be set"):
        CacheConfig(backend="redis")


def test_build_cache_backend_disk(tmp_path):
    backend = build_cache_backend(CacheConfig(disk_root=tmp_path))
    assert backend.name == "disk"


@pytest.mark.skipif(
    not os.getenv("PHYS_PIPELINE_REDIS_URL"), reason="PHYS_PIPELINE_REDIS_URL not set"
)
def test_redis_cache_roundtrip():
    redis_url = os.environ["PHYS_PIPELINE_REDIS_URL"]
    pytest.importorskip("redis")
    from phys_pipeline.cache_redis import RedisCache

    meta, arrays = _sample_payload()
    cache = RedisCache(redis_url, prefix="phys-pipeline-test", ttl_s=5)
    cache.put("k2", meta, arrays)
    restored = cache.get("k2")
    assert restored is not None
    assert restored["meta"] == meta
    np.testing.assert_allclose(restored["arrays"]["x"], arrays["x"])
    np.testing.assert_allclose(restored["arrays"]["y"], arrays["y"])
