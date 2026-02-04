from __future__ import annotations

import copy
import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

import numpy as np
from pydantic import BaseModel, Field

from .policy import PolicyBag

#                                                                Data types

# --- PipelineStage ---

S_contra = TypeVar("S_contra", bound="State", contravariant=True)
C_co = TypeVar("C_co", bound="StageConfig", covariant=True)


class PipelineStage(ABC, Generic[S_contra, C_co]):
    """Abstract process or "stage" in a simulation pipeline.

    Implementations should be deterministic and side-effect free so that
    caching and provenance are reliable.

    Inputs:
        - ``StageConfig``: typed configuration for the stage.
        - ``State``: application payload passed through the pipeline.
        - ``policy``: optional run-wide overrides (see ``PolicyBag``).

    Output:
        - ``StageResult`` containing the updated state plus metrics/artifacts.
    """

    cfg: C_co

    def __init__(self, cfg: C_co):
        self.cfg = cfg

    @abstractmethod
    def process(self, state: S_contra, *, policy: PolicyBag | None = None) -> StageResult:
        """Pure transform: no global side effects, deterministic."""
        ...

    # Optional methods to aid scheduler
    def estimated_cost(self) -> float:
        return 1.0

    def can_parallelize_over(self) -> str | None:
        return None  # key for internal parallelism, if possible (ex: ray)


# --- PipelineStage I/O ---


class StageConfig(BaseModel):
    """Typed, immutable configuration for a stage.

    Subclasses should define the stage parameters, which remain frozen to
    ensure stable hashing and reproducibility.
    """

    model_config = {"arbitrary_types_allowed": True, "frozen": True}
    name: str = "stage cfg"
    # metadata for schedulers and test camapgins eg: "Requires GPU"
    tags: dict[str, Any] = Field(default_factory=dict)


@dataclass(slots=True)
class StageResult:
    """Outputs emitted by a stage.

    Attributes:
        state: Updated state passed to the next stage (e.g., ray vectors).
        metrics: Cheap scalar outputs for reporting or optimization.
        artifacts: Large or diagnostic outputs (plots, traces).
        provenance: Metadata used for caching and auditability.
    """

    state: State
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)


class State(ABC):
    """Application-specific payload that flows through the pipeline."""

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
    """A minimal ready-to-use state suitable for many simulations."""

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
    """DAG node specification used by the future builder/scheduler."""

    id: str
    deps: list[str]  # dependencies
    op_name: str  # operation name
    version: str
