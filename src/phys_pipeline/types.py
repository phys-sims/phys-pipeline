from __future__ import annotations

import copy
import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

import numpy as np
from pydantic import BaseModel, Field

#                                                                Data types

# --- PipelineStage ---

S = TypeVar("S", bound="State")
C = TypeVar("C", bound="StageConfig")


class PipelineStage(ABC, Generic[S, C]):
    """
    PipelineStage is an abstract process or "stage" in a simulation pipeline

    Input:
        StageConfig: holds parameters to design the stage
        State: the object the stage operates on and passes to next stage in the pipeline
    Output:
        StageResult: holds outputs of the stage
    """

    cfg: C

    def __init__(self, cfg: C):
        self.cfg = cfg

    @abstractmethod
    def process(self, state: S) -> StageResult:
        """Pure Transform: no global side effects, deterministic"""  # Safe parallelism and caching
        ...

    # Optional methods to aid scheduler
    def estimated_cost(self) -> float:
        return 1.0

    def can_parallelize_over(self) -> str | None:
        return None  # key for internal parallelism, if possible (ex: ray)


# --- PipelineStage I/O ---


class StageConfig(BaseModel):
    """
    StageConfig configures stages in the pipeline

    The subclass specifies typed parameters to do such

    """

    model_config = {"arbitrary_types_allowed": True, "frozen": True}
    name: str = "stage cfg"
    # metadata for schedulers and test camapgins eg: "Requires GPU"
    tags: dict[str, Any] = Field(default_factory=dict)


@dataclass
class StageResult:
    """
    StageResult contains the outputs of a stage

    state:
        The updated State obj that is passed to the next Stage in the pipeline
        Ex: an updated ray vector - the output of an optic "stage" in raytracing

    metrics:
        Cheap outputs for post-pipeline math or optimization
        Ex: GDD, energy loss

    artifacts:
        Expensive outputs for debugging or logging
        Ex: plots, intermediate step traces

    provenance:
        Record of how the Stage produced StageResult - used for cache key
        Ex: input State hash, StageConfig hash

    """

    state: State
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)


class State(ABC):
    """
    State is an application specific payload that passes through the pipeline

    Example:
        - A ray vector in a raytracing pipeline

    """

    @abstractmethod
    def deepcopy(self) -> State: ...

    @abstractmethod
    def hashable_repr(self) -> bytes: ...


def hash_ndarray(a: np.ndarray) -> bytes:
    a = np.ascontiguousarray(a)
    h = hashlib.sha256()
    h.update(str(a.dtype).encode())
    h.update(str(a.shape).encode())
    h.update(a.data)
    return h.digest()


def hash_small(obj: Any) -> bytes:
    try:
        payload = json.dumps(obj, sort_keys=True, default=str).encode()
    except Exception:
        payload = str(obj).encode()
    return hashlib.sha256(payload).digest()


class SimpleState(State):
    """A tiny ready-to-use state suitable for many sims."""

    def __init__(self, payload: Any = None, meta: dict[str, Any] | None = None):
        self.payload = payload
        self.meta = meta or {}

    def deepcopy(self) -> SimpleState:
        return copy.deepcopy(self)

    def hashable_repr(self) -> bytes:
        h = hashlib.sha256()
        # Hash payload if array-like or json-like
        if hasattr(self.payload, "dtype") and hasattr(self.payload, "shape"):
            h.update(hash_ndarray(self.payload))
        elif self.payload is not None:
            h.update(hash_small(self.payload))
        # Hash a few meta keys if present (common axes)
        for k in ("omega", "x", "y", "t"):
            if k in self.meta and hasattr(self.meta[k], "dtype"):
                h.update(hash_ndarray(self.meta[k]))
        return h.digest()


# --- DAG utility --- WIP


# DAG node
class NodeSpec:
    id: str
    deps: list[str]  # dependencies
    op_name: str  # operation name
    version: str
