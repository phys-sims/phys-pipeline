# ADR-0011: PolicyBag for run-wide overrides

- Status: Proposed
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
