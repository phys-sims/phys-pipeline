**Title:** Stage contract error policy
**ADR ID:** 0010
**Status:** Proposed
**Date:** 2026-02-03

**Context:** Contract violations should be surfaced early so simulation authors can fix their stages before running expensive experiments.

**Options:**
- **A:** Raise explicit `StageContractError` for known contract violations.
- **B:** Allow violations to pass silently and rely on downstream failures.

**Decision:** Choose **A** to make errors actionable and immediate.

**Consequences:**
- Metrics must be scalar and artifacts must respect the recording contract.
- Developers see clear exceptions during development and testing.

**References:**
- `src/phys_pipeline/errors.py`
- `src/phys_pipeline/accumulator.py`

---
