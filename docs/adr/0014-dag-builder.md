**Title:** DAG builder and validation for pipeline graphs
**ADR ID:** ADR-0014
**Status:** Proposed
**Date:** 2026-02-03

**Area:** phys-pipeline
**Tags:** architecture
**Scope:** repo
**Visibility:** public
**Canonical ADR:** phys-pipeline/docs/adr/0014-dag-builder.md

**Context:** Sequential pipelines are useful, but real simulations often branch, join, and share intermediate outputs. We need a DAG representation with validation (cycle detection, missing dependencies) before executing.

**Options:**
- **A:** Define an internal DAG builder using `NodeSpec` with explicit dependency lists and validation helpers.
- **B:** Require users to supply a pre-built graph from a third-party library (e.g., networkx).

**Decision:** Choose **A** to keep the API lightweight and avoid new dependencies while still enabling graph validation.

**Consequences:**
- A builder will normalize nodes, verify dependency IDs, and emit a topological order.
- Validation errors become first-class pipeline errors before execution.

**References:**
- `src/phys_pipeline/types.py` (NodeSpec placeholder)
- ADR-0002 (sequential baseline)

---
