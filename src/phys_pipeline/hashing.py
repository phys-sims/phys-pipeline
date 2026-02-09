import hashlib
import json
from collections.abc import Mapping
from typing import Any

import numpy as np
from pydantic import BaseModel

from .types import State

# --- Hashing utility ---


def stable_json(obj: dict) -> bytes:
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


def hash_dag_node(
    *,
    node_id: str,
    op_name: str,
    version: str,
    cfg_hash: str | None,
    input_hash: str,
    dep_hashes: dict[str, str],
    policy_hash: str | None,
    cache_version: str = "v2",
) -> str:
    payload = {
        "cache_version": cache_version,
        "node_id": node_id,
        "op_name": op_name,
        "version": version,
        "cfg_hash": cfg_hash,
        "input_hash": input_hash,
        "dep_hashes": dict(sorted(dep_hashes.items())),
        "policy_hash": policy_hash,
    }
    return hashlib.sha256(stable_json(payload)).hexdigest()
