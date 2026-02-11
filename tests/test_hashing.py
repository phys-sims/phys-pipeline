from __future__ import annotations

import pytest

from phys_pipeline.hashing import hash_dag_node, hash_model, hash_policy, hash_state
from phys_pipeline.policy import PolicyBag
from phys_pipeline.types import SimpleState, StageConfig


class HashCfg(StageConfig):
    alpha: int = 1
    beta: str = "x"


@pytest.mark.fast
def test_hash_policy_is_order_independent():
    a = PolicyBag({"sampling.N": 4, "sampling.mode": "auto"})
    b = PolicyBag({"sampling.mode": "auto", "sampling.N": 4})
    assert hash_policy(a) == hash_policy(b)


@pytest.mark.fast
def test_hash_model_is_stable_for_same_values():
    cfg1 = HashCfg(name="hash", alpha=3, beta="y")
    cfg2 = HashCfg(name="hash", alpha=3, beta="y")
    assert hash_model(cfg1) == hash_model(cfg2)


@pytest.mark.fast
def test_hash_state_is_deterministic():
    state = SimpleState(payload=5)
    assert hash_state(state) == hash_state(state.deepcopy())


@pytest.mark.fast
def test_hash_dag_node_is_stable():
    key1 = hash_dag_node(
        node_id="node",
        op_name="op",
        version="v2",
        cfg_hash="cfg",
        input_hash="input",
        dep_hashes={"a": "1", "b": "2"},
        policy_hash=None,
    )
    key2 = hash_dag_node(
        node_id="node",
        op_name="op",
        version="v2",
        cfg_hash="cfg",
        input_hash="input",
        dep_hashes={"b": "2", "a": "1"},
        policy_hash=None,
    )
    assert key1 == key2
