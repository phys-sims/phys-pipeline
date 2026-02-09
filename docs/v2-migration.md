# v1 → v2 Migration Guide

This guide summarizes the changes required to move from v1 sequential pipelines to v2 DAG
features. Sequential pipelines remain fully supported; DAG APIs are additive.

## What stays the same
- `SequentialPipeline`, `PipelineStage`, and `StageResult` keep their v1 behavior.
- Stage configs remain frozen Pydantic models (`StageConfig`).
- Artifact recording and policies are unchanged.

## What’s new in v2
- **DAG execution** via `DagExecutor` and `NodeSpec`.
- **Scheduler abstraction** with a default `LocalScheduler`.
- **DAG-aware cache keys** via `DagCache` + `DiskCache` / `SharedDiskCache`.
- **Resource metadata** (`NodeResources`) for CPU/GPU/MPI slots.
- **Parameter sweeps** via `expand_sweep`.
- **ML artifact packaging** via `ModelArtifactPackager`.
- **HPC adapters** (`SlurmScheduler`, `PbsScheduler`, `MockHpcScheduler`).

## Migration steps

### 1. Keep v1 pipelines unchanged (if sequential is enough)
No changes are required for existing `SequentialPipeline` workflows.

### 2. Move to DAG nodes
Wrap existing stages in `NodeSpec` objects and wire dependencies explicitly.

```python
from phys_pipeline.executor import DagExecutor
from phys_pipeline.scheduler import LocalScheduler
from phys_pipeline.types import NodeSpec, SimpleState

nodes = [
    NodeSpec(id="a", stage=StageA(StageACfg())),
    NodeSpec(id="b", deps=["a"], stage=StageB(StageBCfg())),
]

executor = DagExecutor(scheduler=LocalScheduler(max_workers=2, max_cpu=2))
result = executor.run(SimpleState(payload=None), nodes)
```

### 3. Enable caching (optional)
Provide a `DagCache` wrapper around a cache backend.

```python
from phys_pipeline.cache import DiskCache
from phys_pipeline.dag_cache import DagCache

cache = DagCache(DiskCache(".cache/phys-v2"))
executor = DagExecutor(scheduler=LocalScheduler(max_workers=2, max_cpu=2), cache=cache)
```

### 4. Add resource metadata
Specify CPU/GPU/MPI requirements on `NodeResources`.

```python
from phys_pipeline.types import NodeResources, NodeSpec

gpu_node = NodeSpec(
    id="train",
    stage=TrainStage(TrainCfg()),
    resources=NodeResources(cpu=4, gpu=1),
)
```

## Deprecations and compatibility notes
- No v1 APIs are removed in v2.
- DAG caching relies on pickling `State`. If your state is not picklable, disable caching or
  provide a custom state serialization strategy.

## Testing upgrade
Continue running the offline-safe checks:

```bash
python -m ruff check .
python -m black --check .
python -m mypy
python -m pytest -q -m "not slow"
```
