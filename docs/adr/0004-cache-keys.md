**Title:** State hashing and cache key composition
**ADR ID:** 0004
**Status:** Proposed
**Date:** 2026-02-03

**Context:** Reproducible simulations need stable cache keys across runs and environments. Keys must capture the state, configuration, and policy inputs that influence outputs.

**Options:**
- **A:** Cache key = state hash + config hash + stage version + policy hash.
- **B:** Cache key = state hash only; rely on manual invalidation.

**Decision:** Choose **A** to minimize false hits and make invalidation explicit.

**Consequences:**
- Custom state types must implement `hashable_repr`.
- Configs are frozen to keep hashes stable.
- Policy changes automatically invalidate cache entries.

**References:**
- `src/phys_pipeline/types.py`
- `src/phys_pipeline/hashing.py`

---
