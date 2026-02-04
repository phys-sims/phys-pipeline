# phys-pipeline

A lightweight runtime framework for building, validating, and executing physics simulation pipelines as modular DAGs of typed stages.

## Why phys-pipeline

- **Typed stage contracts** for reproducible simulations.
- **Deterministic execution** with a simple sequential pipeline baseline.
- **Provenance and caching hooks** for stable cache keys and audit trails.
- **Artifact recording** that keeps results lightweight until you opt in.

## Installation

```bash
pip install -e .
```

## Quickstart

```python
from phys_pipeline.pipeline import SequentialPipeline
from phys_pipeline.types import PipelineStage, StageConfig, StageResult, SimpleState


class MultiplyConfig(StageConfig):
    factor: float = 2.0


class MultiplyStage(PipelineStage[SimpleState, MultiplyConfig]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult:
        new_state = state.deepcopy()
        new_state.payload = new_state.payload * self.cfg.factor
        return StageResult(state=new_state, metrics={"factor": self.cfg.factor})


pipeline = SequentialPipeline([
    MultiplyStage(MultiplyConfig(factor=3.0)),
])

result = pipeline.run(SimpleState(payload=10))
print(result.state.payload)  # 30
print(result.metrics)
```

## Concepts

### Pipeline stages

Stages are pure transforms that accept a `State` object and return a `StageResult`. Use `StageConfig` for typed, immutable configuration and override `process` for the core logic. See `src/phys_pipeline/types.py` for the base interfaces.

### Running a pipeline

`SequentialPipeline` validates and executes stages in order. For DAG-shaped workflows, build a `Dag` and run it with `DagPipeline` plus a scheduler such as `TopoScheduler` to deterministically traverse the DAG. You can also wrap pipelines inside other pipelines using `PipelineStageWrapper` for composition (ADR-0008).

### Artifact recording

Artifacts (plots, large arrays) are recorded only when requested. Enable recording via `SequentialPipeline.run(record_artifacts=True, recorder=...)`.

### Policies

Use `PolicyBag` for run-wide overrides like tolerances or instrumentation flags. Policies are hashed into provenance so cache keys remain stable.

## Documentation

- Architecture decisions: [`docs/adr/INDEX.md`](docs/adr/INDEX.md)
- How to build simulations: [`docs/how-to-build-simulations.md`](docs/how-to-build-simulations.md)

## Roadmap (DAG execution)

Planned work includes richer DAG builders, schedulers, and executor abstractions. See ADRs 0014–0016 for details.

## License

MIT. See [`LICENSE`](LICENSE).
