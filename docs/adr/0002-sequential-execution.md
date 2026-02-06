**Title:** Sequential pipeline execution model
**ADR ID:** ADR-0002
**Status:** Proposed
**Date:** 2026-02-03

**Area:** phys-pipeline
**Tags:** architecture
**Scope:** repo
**Visibility:** public
**Canonical ADR:** phys-pipeline/docs/adr/0002-sequential-execution.md

**Context:** The runtime executes stages in order today. A DAG runner is hinted in code, but there is no scheduler or executor yet. We need a clear, deterministic execution model while the DAG work is designed.

**Options:**
- **A:** Sequential execution only, with pipeline composition for reuse.
- **B:** Implement full DAG execution immediately.
- **C:** Support both models with a pluggable scheduler abstraction from day one.

**Decision:** Choose **A** now to ship a predictable baseline, and leave DAG scheduling for dedicated ADRs.

**Consequences:**
- Straight-line execution is easy to reason about and test.
- Composition relies on pipeline-as-stage rather than parallel scheduling.
- Future DAG work must preserve sequential semantics for debugging.

**References:**
- `src/phys_pipeline/pipeline.py`
- ADR-0008 (pipeline-as-stage)

---
