from __future__ import annotations

import pytest

from phys_pipeline.hashing import hash_model, hash_policy
from phys_pipeline.policy import PolicyBag
from phys_pipeline.types import StageConfig


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
