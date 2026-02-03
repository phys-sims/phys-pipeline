**Title:** PolicyBag for run-wide overrides
**ADR ID:** 0011
**Status:** Accepted
**Date:** 2026-02-03

**Context:** Simulations need optional run-level overrides (e.g., tolerances, instrumentation flags) without hard-coding globals or mutating stage configs.

**Options:**
- **A:** Pass a `PolicyBag` through the pipeline to each stage.
- **B:** Store policy as a global singleton.

**Decision:** Choose **A** to keep behavior explicit and testable.

**Consequences:**
- Stages can opt into policy overrides.
- `policy_hash` is included in provenance for cache validation.

**References:**
- `src/phys_pipeline/policy.py`
- `src/phys_pipeline/pipeline.py`

---
