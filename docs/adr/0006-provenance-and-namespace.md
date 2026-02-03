**Title:** Metrics namespace and provenance schema
**ADR ID:** 0006
**Status:** Proposed
**Date:** 2026-02-03

**Context:** Metrics and artifacts from multiple stages must be comparable and traceable across runs. A consistent namespace and provenance schema enables debugging and cache validation.

**Options:**
- **A:** Namespace metrics/artifacts by pipeline + stage; record provenance fields (version, hashes, timing).
- **B:** Allow each stage to choose its own naming conventions and provenance fields.

**Decision:** Choose **A** to enforce consistent aggregation and simplify downstream analytics.

**Consequences:**
- Output keys are predictable for reporting.
- Provenance can be used for audit trails and caching decisions.

**References:**
- `src/phys_pipeline/accumulator.py`
- `src/phys_pipeline/pipeline.py`

---
