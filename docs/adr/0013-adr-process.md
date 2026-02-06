**Title:** ADR process and indexing
**ADR ID:** ADR-0013
**Status:** Proposed
**Date:** 2026-02-03

**Area:** phys-pipeline
**Tags:** architecture
**Scope:** repo
**Visibility:** public
**Canonical ADR:** phys-pipeline/docs/adr/0013-adr-process.md

**Context:** ADRs must remain consistent and discoverable as the project grows. We need a predictable template and index update workflow.

**Options:**
- **A:** Use the provided ADR templates and `scripts/adr_tools.py` for creation and indexing.
- **B:** Allow free-form ADRs and manual index edits.

**Decision:** Choose **A** to keep documentation consistent and searchable.

**Consequences:**
- New ADRs should be created via `scripts/adr_tools.py`.
- The index must be updated whenever ADRs are added or removed.

**References:**
- `scripts/adr_tools.py`
- `docs/adr/_template-full.md`
- `docs/adr/_template-lite.md`

---
