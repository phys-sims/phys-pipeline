# ADR-0006: Metrics namespace and provenance schema

- Status: Proposed
- Date: 2026-02-03
- Deciders: @tbd
- Area: phys-pipeline
- Related: src/phys_pipeline/accumulator.py, src/phys_pipeline/pipeline.py
- Tags: observability, data-model

## Decision
- Metrics and artifacts are namespaced by pipeline and stage.
- Provenance includes stage, version, config hash, timing, and policy hash (when provided).

## Consequences
- Outputs are readable and comparable across runs
- Provenance can be used for cache validation and audit
