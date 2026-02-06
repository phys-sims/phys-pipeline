**Title:** Testing strategy for physics and engineering validation
**ADR ID:** ADR-0012
**Status:** Proposed
**Date:** 2026-02-03

**Area:** phys-pipeline
**Tags:** architecture
**Scope:** repo
**Visibility:** public
**Canonical ADR:** phys-pipeline/docs/adr/0012-testing-strategy.md

**Context:** Physics pipelines require both software correctness and scientific validity. Tests must cover local behavior, integration, and reference-validated outcomes.

**Options:**
- **A:** Three-tier strategy: unit tests, pipeline integration tests, physics validation tests.
- **B:** Only unit tests and ad-hoc notebooks.

**Decision:** Choose **A** to keep correctness and scientific validity visible in CI.

**Consequences:**
- New stages should ship with unit tests.
- Reference/physics tests may run in a separate CI job due to runtime costs.

**References:**
- `tests/test_smoke.py`
- `docs/issue-templates-guide.md`

---
