# ADR-0003: Stage contract and StageResult emissions

- Status: Proposed
- Date: 2026-02-03
- Deciders: @tbd
- Area: phys-pipeline
- Related: src/phys_pipeline/types.py, src/phys_pipeline/accumulator.py
- Tags: api, data-model

## Context
Stages are the core abstraction. The repo assumes purity and a structured output via `StageResult`.

## Decision
- `PipelineStage.process` is a pure transform with no global side effects.
- Stage outputs are in `StageResult` with:
  - `state` for pipeline flow
  - `metrics` for scalar results
  - `artifacts` for heavier outputs
  - `provenance` for hashing and audit

## Consequences
- Metrics must be scalar; arrays go to `state.meta` or `artifacts`.
- Contract violations raise `StageContractError`.
