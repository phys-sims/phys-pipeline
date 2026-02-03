# ADR-0012: Testing strategy for physics and engineering validation

- Status: Proposed
- Date: 2026-02-03
- Deciders: @tbd
- Area: phys-pipeline
- Related: tests/test_smoke.py, .github/ISSUE_TEMPLATE/test.yml
- Tags: testing, validation

## Decision
Adopt a 3-tier test strategy:
- Unit tests for stage behavior
- Integration tests for pipelines
- Physics validation tests tied to references or tolerances

## Consequences
- Clear expectation for test coverage and artifacts
- Aligns with issue templates and ADRs
