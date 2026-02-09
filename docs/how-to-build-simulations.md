# How to build physics simulations with phys-pipeline

This guide shows how to build a physics simulation as a modular pipeline
of typed stages.

## 1. Install for local dev
```bash
pip install -e .
```

## 2. Define a State
State carries the physics payload across stages.

```python
from phys_pipeline.types import State
import copy, hashlib, json

class MyState(State):
    def __init__(self, payload, meta=None):
        self.payload = payload
        self.meta = meta or {}

    def deepcopy(self):
        return copy.deepcopy(self)

    def hashable_repr(self) -> bytes:
        return hashlib.sha256(json.dumps(self.meta, sort_keys=True).encode()).digest()
```

You can also use `SimpleState` from `phys_pipeline.types` for quick starts.

## 3. Define StageConfig and Stage
Stages are pure transforms from state to state.

```python
from phys_pipeline.policy import PolicyBag
from phys_pipeline.types import PipelineStage, StageConfig, StageResult, SimpleState

class FreqCfg(StageConfig):
    N: int
    center: float
    span: float

class FreqStage(PipelineStage[SimpleState, FreqCfg]):
    def process(self, state: SimpleState, *, policy: PolicyBag | None = None) -> StageResult:
        import numpy as np
        w = self.cfg.center + np.linspace(-self.cfg.span, self.cfg.span, self.cfg.N)
        st = state.deepcopy()
        st.meta["omega"] = w
        return StageResult(state=st)
```

## 4. Build and run the pipeline
```python
from phys_pipeline.pipeline import SequentialPipeline
from phys_pipeline.types import SimpleState, StageConfig

pipe = SequentialPipeline([
    FreqStage(FreqCfg(name="freq", N=2048, center=0.02, span=1e-3)),
    # add more stages here
], name="demo")

out = pipe.run(SimpleState(payload=None))
print(out.metrics)
```

## 4b. Build and run a DAG
Use `DagExecutor` for branched graphs. Nodes can depend on multiple parents; in that case the
node receives a `DagState` wrapper with inputs keyed by node id.

```python
from phys_pipeline.executor import DagExecutor
from phys_pipeline.scheduler import LocalScheduler
from phys_pipeline.types import DagState, NodeSpec, SimpleState

class MergeStage(PipelineStage[DagState, StageConfig]):
    def process(self, state: DagState, *, policy: PolicyBag | None = None) -> StageResult:
        total = sum(s.payload for s in state.inputs.values())
        return StageResult(state=SimpleState(payload=total))

nodes = [
    NodeSpec(id="a", stage=FreqStage(FreqCfg(name="a", N=3, center=0.1, span=0.01))),
    NodeSpec(id="b", deps=["a"], stage=FreqStage(FreqCfg(name="b", N=5, center=0.1, span=0.02))),
    NodeSpec(id="c", deps=["a"], stage=FreqStage(FreqCfg(name="c", N=7, center=0.1, span=0.03))),
    NodeSpec(id="merge", deps=["b", "c"], stage=MergeStage(StageConfig())),
]

executor = DagExecutor(scheduler=LocalScheduler(max_workers=2, max_cpu=2))
out = executor.run(SimpleState(payload=None), nodes)
print(out.execution_order)
```

## 5. Optional policy overrides
Use a `PolicyBag` to provide run-wide overrides without rebuilding the pipeline.
Stages receive an optional `policy` argument on `process` and can ignore it when unused.

```python
from phys_pipeline.policy import PolicyBag

class FreqStage(PipelineStage[SimpleState, FreqCfg]):
    def process(self, state: SimpleState, *, policy: PolicyBag | None = None) -> StageResult:
        import numpy as np
        N = int(policy.get("freq.N", self.cfg.N)) if policy else self.cfg.N
        w = self.cfg.center + np.linspace(-self.cfg.span, self.cfg.span, N)
        st = state.deepcopy()
        st.meta["omega"] = w
        return StageResult(state=st)

policy = PolicyBag({"freq.N": 4096})
out = pipe.run(SimpleState(payload=None), policy=policy)
print(out.provenance["policy_hash"])  # useful for cache keys

# Or set it once on the pipeline:
pipe.set_policy(policy)
out = pipe.run(SimpleState(payload=None))
```

## 6. Emit metrics and artifacts
Metrics must be scalar. Artifacts can be plots or heavier blobs.

```python
class FitCfg(StageConfig):
    degree: int = 2

class FitStage(PipelineStage[SimpleState, FitCfg]):
    def process(self, state: SimpleState, *, policy: PolicyBag | None = None) -> StageResult:
        import numpy as np
        w = state.meta["omega"]
        coefs = np.polyfit(w - w.mean(), w, deg=self.cfg.degree)

        def plot():
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.plot(w, w)
            return fig

        st = state.deepcopy()
        st.meta["fit_coefs"] = coefs
        return StageResult(
            state=st,
            metrics={"fit.degree": float(self.cfg.degree)},
            artifacts={"fit.plot": plot},
        )
```

## 7. Save artifacts
Use the artifact recorder to save plots or blobs.

```python
from phys_pipeline.record import ArtifactRecorder
from pathlib import Path

rec = ArtifactRecorder(Path("artifacts"))
out = pipe.run(SimpleState(None), record_artifacts=True, recorder=rec)
```

## 8. Testing and validation
See `tests/test_smoke.py` for an end-to-end example pipeline with metrics
and artifact recording.

## 9. Cache backends
phys-pipeline ships a disk cache format (JSON + NPZ) and an optional Redis backend. Disk remains
the default; Redis is opt-in.

```python
from pathlib import Path
from phys_pipeline.cache import CacheConfig, build_cache_backend

disk_cache = build_cache_backend(CacheConfig(disk_root=Path(".cache/phys")))

redis_cache = build_cache_backend(
    CacheConfig(
        backend="redis",
        redis_url="redis://localhost:6379/0",
        redis_prefix="phys-pipeline",
        redis_ttl_s=3600,
    )
)
```

Redis usage requires installing the `redis` client package (`pip install redis`) and setting a
reachable `redis_url`.

## 10. DAG cache, sweeps, and schedulers

Use `DagCache` to enable v2 cache keys, and `expand_sweep` to expand parameter sweeps.

```python
from phys_pipeline.cache import DiskCache
from phys_pipeline.dag_cache import DagCache
from phys_pipeline.sweep import SweepSpec, expand_sweep

cache = DagCache(DiskCache(Path(".cache/phys-v2")))
nodes = expand_sweep(
    nodes,
    [SweepSpec(node_id="b", param_grid={"N": [512, 1024, 2048]})],
)
executor = DagExecutor(scheduler=LocalScheduler(max_workers=4, max_cpu=4), cache=cache)
out = executor.run(SimpleState(payload=None), nodes)
```
