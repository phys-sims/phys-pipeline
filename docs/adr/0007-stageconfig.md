# ADR-0007: StageConfig uses frozen Pydantic models

- Status: Proposed
- Date: 2026-02-03
- Deciders: @tbd
- Area: phys-pipeline
- Related: src/phys_pipeline/types.py
- Tags: api, config

## Decision
Use frozen `BaseModel` configs with `arbitrary_types_allowed` to enable
stable hashing and strong typing.

## Consequences
- Configs are immutable and hashable
- Arbitrary types (arrays, callables) are allowed by design
