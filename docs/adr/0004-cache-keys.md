# ADR-0004: State hashing and cache key composition

- Status: Proposed
- Date: 2026-02-03
- Deciders: @tbd
- Area: phys-pipeline
- Related: src/phys_pipeline/types.py, src/phys_pipeline/hashing.py
- Tags: caching, reproducibility

## Context
Caching requires stable keys across runs and environments.

## Decision
Cache keys combine:
- `State.hashable_repr()`
- `StageConfig` hash via `hash_model`
- Stage version label if provided
- Policy hash when a run-wide policy is supplied

## Consequences
- Users must implement `hashable_repr` for custom state
- Configs are frozen to ensure stable hashes
- Cache invalidates when policy changes
