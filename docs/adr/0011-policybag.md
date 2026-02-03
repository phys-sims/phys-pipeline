# ADR-0011: PolicyBag for run-wide overrides

- Status: Accepted
- Date: 2026-02-03
- Deciders: @tbd
- Area: phys-pipeline
- Related: src/phys_pipeline/policy.py
- Tags: configuration, runtime

## Decision
Use `PolicyBag` for optional run-wide parameters, leaving
stage behavior explicit and local.

## Consequences
- Avoids hidden globals
- Allows cross-cutting behaviors without refactoring APIs

## Implementation Notes
- `SequentialPipeline.run(..., policy=PolicyBag)` passes `policy` into every stage `process` call
- `policy_hash` is attached to provenance for cache validation
