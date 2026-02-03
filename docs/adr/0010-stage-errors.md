# ADR-0010: Stage contract error policy

- Status: Proposed
- Date: 2026-02-03
- Deciders: @tbd
- Area: phys-pipeline
- Related: src/phys_pipeline/errors.py, src/phys_pipeline/accumulator.py
- Tags: errors, api

## Decision
Violations of the stage contract raise `StageContractError`, specifically:
- non-scalar metrics
- invalid artifact type usage (when previewing)

## Consequences
- Errors are discoverable at development time
- Helps keep metrics aggregation safe
