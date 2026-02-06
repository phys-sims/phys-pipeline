**Title:** StageConfig uses frozen Pydantic models
**ADR ID:** ADR-0007
**Status:** Proposed
**Date:** 2026-02-03

**Area:** phys-pipeline
**Tags:** architecture
**Scope:** repo
**Visibility:** public
**Canonical ADR:** phys-pipeline/docs/adr/0007-stageconfig.md

**Context:** Stages need strongly typed configuration objects that are immutable and hashable for caching. We also need to allow scientific data types (arrays, callables) in configs.

**Options:**
- **A:** Use frozen `pydantic.BaseModel` with `arbitrary_types_allowed`.
- **B:** Use mutable dataclasses and rely on manual hashing.

**Decision:** Choose **A** to get validation plus stable hashing by default.

**Consequences:**
- Configs are immutable, ensuring reproducible runs.
- Non-JSON types can still be embedded when needed.

**References:**
- `src/phys_pipeline/types.py`

---
