**Title:** Testing error taxonomy for simulations
**ADR ID:** ADR-0017
**Status:** Proposed
**Date:** 2026-02-03

**Area:** phys-pipeline
**Tags:** architecture
**Scope:** repo
**Visibility:** public
**Canonical ADR:** phys-pipeline/docs/adr/0017-testing-error-taxonomy.md

**Context:** Tests need to distinguish between contract violations, runtime failures, and scientific validation failures. Without a taxonomy, failures are harder to triage and to automate in CI.

**Options:**
- **A:** Document a taxonomy that maps expected failures to existing error types and test markers.
- **B:** Treat all failures as generic exceptions and rely on manual inspection.

**Decision:** Choose **A** to make CI reporting actionable and to clarify expected vs unexpected failures.

**Consequences:**
- Contract violations use `StageContractError` (ADR-0010).
- Runtime execution failures use `PipelineError` subclasses.
- Physics/validation failures are asserted explicitly in tests with clear tolerances.

**References:**
- `src/phys_pipeline/errors.py`
- ADR-0012 (testing strategy)

---
