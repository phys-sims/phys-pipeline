**Title:** Stage contract error policy
**ADR ID:** ADR-0010
**Status:** Proposed
**Date:** 2026-02-03

**Area:** phys-pipeline
**Tags:** architecture
**Scope:** repo
**Visibility:** public
**Canonical ADR:** phys-pipeline/docs/adr/0010-stage-errors.md

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
