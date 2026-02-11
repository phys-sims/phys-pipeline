# v2.0.0 Release Notes

`phys-pipeline` v2.0.0 promotes the DAG/scheduler/cache/tooling work from the v1.x line into a formal major release.

## Highlights

- DAG execution support via `DagExecutor` and typed `NodeSpec` dependencies.
- Local parallel scheduling via `LocalScheduler` resource-aware job execution.
- DAG-native caching via `DagCache` with stable cache hashing inputs.
- Parameter-sweep expansion helpers via `expand_sweep`.
- Optional ML artifact packaging and HPC scheduler adapters.

## Compatibility

- v1 sequential APIs (`SequentialPipeline`, `PipelineStage`, `StageResult`) remain available.
- No v1 APIs were removed as part of v2.0.0.

## Migration guidance

- See [`docs/v2-migration.md`](v2-migration.md) for step-by-step v1 → v2 migration guidance.
- See [`docs/how-to-build-simulations.md`](how-to-build-simulations.md) for end-to-end DAG examples.

## Validation summary for this release prep

- Offline-safe quality checks passed (`ruff`, `black --check`, `mypy`, and non-slow pytest).
- Slow pytest marker suite passed.
- Benchmarks captured for cache and scheduler behavior:
  - Cache benchmark: cold `0.0037s`, warm `0.0005s`.
  - Scheduler benchmark: `0.0112s` for 8 parallel 10ms jobs.
