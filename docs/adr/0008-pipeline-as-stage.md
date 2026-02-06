**Title:** Pipeline-as-stage composition
**ADR ID:** ADR-0008
**Status:** Proposed
**Date:** 2026-02-03

**Area:** phys-pipeline
**Tags:** architecture
**Scope:** repo
**Visibility:** public
**Canonical ADR:** phys-pipeline/docs/adr/0008-pipeline-as-stage.md

**Context:** Teams need to reuse sub-pipelines across scenarios without introducing DAG scheduling yet. Composition should remain explicit and sequential by default.

**Options:**
- **A:** Wrap a pipeline inside a stage so it can be treated as a single unit.
- **B:** Require DAG scheduling for any reuse/composition.

**Decision:** Choose **A** to keep the execution model simple while enabling reuse.

**Consequences:**
- Nested pipelines are possible without a scheduler.
- Pipeline boundaries remain explicit for provenance.

**References:**
- `src/phys_pipeline/pipeline.py`

---
