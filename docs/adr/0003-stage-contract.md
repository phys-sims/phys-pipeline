**Title:** Stage contract and StageResult emissions
**ADR ID:** ADR-0003
**Status:** Proposed
**Date:** 2026-02-03

**Area:** phys-pipeline
**Tags:** architecture
**Scope:** repo
**Visibility:** public
**Canonical ADR:** phys-pipeline/docs/adr/0003-stage-contract.md

**Context:** Stages are the core abstraction for simulations. To enable caching, provenance, and testability, every stage must behave as a pure transform and emit outputs in a consistent structure.

**Options:**
- **A:** Enforce a strict `StageResult` schema with explicit `state`, `metrics`, `artifacts`, and `provenance`.
- **B:** Allow stages to return arbitrary objects and infer structure downstream.

**Decision:** Choose **A** to make data flow explicit, keep cache keys stable, and simplify testing/aggregation.

**Consequences:**
- `PipelineStage.process` must be deterministic and side-effect free.
- Metrics are scalar; large data belongs in `state` or `artifacts`.
- Contract violations raise `StageContractError` (see ADR-0010).

**References:**
- `src/phys_pipeline/types.py`
- `src/phys_pipeline/accumulator.py`

---
