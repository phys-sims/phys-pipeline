**Title:** DiskCache format and lifecycle
**ADR ID:** 0009
**Status:** Proposed
**Date:** 2026-02-03

**Context:** Cached stage outputs should be inspectable and portable across environments. The cache format must support structured metadata alongside array data.

**Options:**
- **A:** Store metadata as JSON and array payloads as compressed NPZ.
- **B:** Store everything in a single pickle file.

**Decision:** Choose **A** to keep caches human-inspectable and robust across Python versions.

**Consequences:**
- Cache entries are easy to diff and debug.
- Invalidations are explicit by removing files.

**References:**
- `src/phys_pipeline/cache.py`

---
