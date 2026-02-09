import hashlib
import json
from collections.abc import Mapping
from typing import Any

import numpy as np
from pydantic import BaseModel

from .types import StageResult, State

DAG_CACHE_VERSION = "dag-v2"

# --- Hashing utility ---


def stable_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def hash_model(model: BaseModel) -> str:
    return hashlib.sha256(stable_json(model.model_dump())).hexdigest()


def hash_policy(policy: Mapping[str, Any]) -> str:
    return hashlib.sha256(stable_json(dict(policy))).hexdigest()


def hash_ndarray(a: np.ndarray) -> bytes:
    a = np.ascontiguousarray(a)
    h = hashlib.sha256()
    h.update(str(a.dtype).encode())
    h.update(str(a.shape).encode())
    h.update(a.data)
    return h.digest()


def digest_many(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode())
    return h.hexdigest()


def hash_state(state: State) -> str:
    return hashlib.sha256(state.hashable_repr()).hexdigest()


def _hash_value(value: Any) -> str:
    if isinstance(value, np.ndarray):
        return hashlib.sha256(hash_ndarray(value)).hexdigest()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return hashlib.sha256(stable_json({"v": value})).hexdigest()
    if isinstance(value, dict):
        return hashlib.sha256(
            stable_json({k: _hash_value(v) for k, v in sorted(value.items())})
        ).hexdigest()
    if isinstance(value, (list, tuple)):
        return hashlib.sha256(stable_json([_hash_value(v) for v in value])).hexdigest()
    if callable(value):
        name = getattr(value, "__name__", value.__class__.__name__)
        return hashlib.sha256(stable_json({"callable": name})).hexdigest()
    return hashlib.sha256(stable_json({"repr": str(value)})).hexdigest()


def hash_stage_result(result: StageResult) -> str:
    payload = {
        "state": hash_state(result.state),
        "metrics": _hash_value(result.metrics or {}),
        "artifacts": _hash_value(result.artifacts or {}),
    }
    return hashlib.sha256(stable_json(payload)).hexdigest()


def hash_dependency_results(results: Mapping[str, StageResult]) -> dict[str, str]:
    return {k: hash_stage_result(v) for k, v in sorted(results.items())}


def hash_dag_node_cache_key(
    *,
    node_id: str,
    stage: Any,
    input_state_hash: str,
    dependency_hashes: Mapping[str, str],
    policy_hash: str | None,
    version: str,
) -> str:
    cfg_hash = ""
    if getattr(stage, "cfg", None) is not None:
        try:
            cfg_hash = hash_model(stage.cfg)
        except Exception:
            cfg_hash = ""
    policy_part = policy_hash or ""
    dep_parts = [f"{k}:{v}" for k, v in sorted(dependency_hashes.items())]
    return digest_many(
        DAG_CACHE_VERSION,
        node_id,
        version,
        cfg_hash,
        policy_part,
        input_state_hash,
        *dep_parts,
    )
