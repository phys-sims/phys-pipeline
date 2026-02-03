# ADR-0008: Pipeline-as-stage composition

- Status: Proposed
- Date: 2026-02-03
- Deciders: @tbd
- Area: phys-pipeline
- Related: src/phys_pipeline/pipeline.py
- Tags: composition, api

## Decision
Support nested pipelines using `PipelineStageWrapper` so pipelines can
compose without DAG scheduling.

## Consequences
- Encourages modular design
- Keeps execution model simple for now
