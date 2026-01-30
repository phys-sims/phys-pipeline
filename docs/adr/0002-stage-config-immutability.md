**Title:** Immutable Pydantic StageConfig
**ADR ID:** 0002-lite
**Status:** Accepted
**Date:** 2026-01-30

**Context:** Stage configuration values should be validated, hashable, and stable across a run to support caching, provenance, and reproducibility.

**Options:**
- **A:** Use immutable Pydantic models (`frozen=True`) for `StageConfig`.
- **B:** Use mutable dataclasses or dicts for `StageConfig`.

**Decision:** Choose **A** so configs are validated, typed, and safe to hash for provenance while preventing accidental mutation during pipeline execution.

**Consequences:** Config changes require explicit new instances, enabling stable cache keys and clearer provenance; callers must avoid in-place edits and update tests/docs when config fields change.

**References:** `src/phys_pipeline/types.py` (`StageConfig`).

---
