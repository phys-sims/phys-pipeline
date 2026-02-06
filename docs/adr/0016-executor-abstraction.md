**Title:** Executor abstraction for running scheduled stages
**ADR ID:** ADR-0016
**Status:** Proposed
**Date:** 2026-02-03

**Area:** phys-pipeline
**Tags:** architecture
**Scope:** repo
**Visibility:** public
**Canonical ADR:** phys-pipeline/docs/adr/0016-executor-abstraction.md

**Context:** The scheduler decides *what* to run, but we still need an execution layer that runs stage computations, captures timings, and handles failures consistently.

**Options:**
- **A:** Introduce an executor interface with a default in-process implementation.
- **B:** Embed execution directly in the scheduler with no separate abstraction.

**Decision:** Choose **A** to keep responsibilities separated and enable future executors (threaded, distributed, GPU-aware).

**Consequences:**
- Executors handle timing, error capture, and provenance updates per stage.
- A consistent execution API simplifies testing and instrumentation.

**References:**
- ADR-0015 (scheduler interface)
- `src/phys_pipeline/pipeline.py`

---
