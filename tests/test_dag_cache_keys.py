from __future__ import annotations

from typing import Any

from phys_pipeline.hashing import (
    hash_dag_node_cache_key,
    hash_dependency_results,
    hash_stage_result,
)
from phys_pipeline.types import PipelineStage, SimpleState, StageConfig, StageResult


class EchoCfg(StageConfig):
    label: str = "echo"


class EchoStage(PipelineStage[SimpleState, EchoCfg]):
    def process(self, state: SimpleState, *, policy: Any | None = None) -> StageResult:
        return StageResult(state=state.deepcopy(), metrics={"label": 1.0})


def test_hash_stage_result_is_deterministic():
    state = SimpleState(payload=3)
    result = StageResult(state=state, metrics={"m": 1.0}, artifacts={"a": "x"})

    assert hash_stage_result(result) == hash_stage_result(result)


def test_hash_dependency_results_orders_by_key():
    state = SimpleState(payload=1)
    a = StageResult(state=state)
    b = StageResult(state=state)

    dep_hashes = hash_dependency_results({"b": b, "a": a})

    assert list(dep_hashes.keys()) == ["a", "b"]


def test_hash_dag_node_cache_key_changes_with_dependency_hash():
    stage = EchoStage(EchoCfg(name="echo"))
    dep_hashes = {"a": "hash-a"}
    dep_hashes_alt = {"a": "hash-b"}

    key = hash_dag_node_cache_key(
        node_id="node",
        stage=stage,
        input_state_hash="state-hash",
        dependency_hashes=dep_hashes,
        policy_hash=None,
        version="v1",
    )
    key_alt = hash_dag_node_cache_key(
        node_id="node",
        stage=stage,
        input_state_hash="state-hash",
        dependency_hashes=dep_hashes_alt,
        policy_hash=None,
        version="v1",
    )

    assert key != key_alt
