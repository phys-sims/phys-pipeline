# ADR-0002: Sequential pipeline execution model

- Status: Proposed
- Date: 2026-02-03
- Deciders: @tbd
- Area: phys-pipeline
- Related: src/phys_pipeline/pipeline.py
- Tags: execution, runtime, design

## Context
The current runtime executes stages in order via `SequentialPipeline`. A DAG runner is hinted in `types.py` but not implemented.

## Options Considered
Option A: Sequential execution only, with optional pipeline composition
Option B: DAG execution now
Option C: Support both with a pluggable scheduler

## Decision
Choose Option A now. Keep DAG runner as a future ADR.

## Consequences
- Clear, deterministic execution model today
- DAG design remains open
- Pipeline-as-stage allows composition without DAG scheduling
