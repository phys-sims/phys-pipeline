**Title:** Scheduler interface for DAG execution
**ADR ID:** 0015
**Status:** Proposed
**Date:** 2026-02-03

**Context:** Once a DAG is defined, we need a scheduler to choose execution order, respect dependencies, and optionally enable concurrency.

**Options:**
- **A:** Define a scheduler interface with a default topological (sequential) scheduler.
- **B:** Implement a parallel scheduler immediately (thread/process pool) without an interface.

**Decision:** Choose **A** to keep execution deterministic while allowing future schedulers (parallel, distributed) to plug in.

**Consequences:**
- The scheduler contract will select runnable nodes based on completed dependencies.
- Initial scheduling remains deterministic and reproducible for debugging.

**References:**
- ADR-0014 (DAG builder)
- ADR-0002 (sequential baseline)

---
