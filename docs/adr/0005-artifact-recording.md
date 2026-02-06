**Title:** Artifact recording and storage formats
**ADR ID:** ADR-0005
**Status:** Proposed
**Date:** 2026-02-03

**Area:** phys-pipeline
**Tags:** architecture
**Scope:** repo
**Visibility:** public
**Canonical ADR:** phys-pipeline/docs/adr/0005-artifact-recording.md

**Context:** Some simulation outputs are large (plots, intermediate arrays) and should not be stored in memory by default. We need an opt-in recording system that preserves artifacts without bloating results.

**Options:**
- **A:** Record artifacts only when explicitly requested, persist to disk with lightweight previews in results.
- **B:** Always keep artifacts in-memory for convenience.

**Decision:** Choose **A** to keep the default pipeline results lightweight and predictable.

**Consequences:**
- Recording must be enabled via pipeline run options.
- Results store artifact references/paths when recording is on.
- Storage formats are standardized for interoperability (e.g., PNG, JSON).

**References:**
- `src/phys_pipeline/record.py`
- `src/phys_pipeline/accumulator.py`

---
