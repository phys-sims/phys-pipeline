**Title:** Cache backends = disk + redis with timing metrics

- **ADR ID:** `ADR-0019`
- **Status:** `Proposed`
- **Date:** `2026-02-07`
- **Deciders:** `@phys-pipeline-maintainers`
- **Area:** `phys-pipeline`
- **Related:** `ADR-0004, ADR-0009`
- **Tags:** `performance, api, data-model, ops`
- **Scope:** `repo`
- **Visibility:** `public`
- **Canonical ADR:** `phys-pipeline/docs/adr/0019-cache-backend-options-and-performance-instrumentation.md`
- **Impacted repos:** `phys-pipeline`
- **Related ecosystem ADRs:** `N/A`

### Context
- **Problem statement.** The project needs user-selectable cache storage that works both for local
  workflows and shared/cloud runs, while exposing storage/lookup latency to inform tuning and
  pipeline diagnostics.
- **In/Out of scope.** This ADR covers cache backend options and timing instrumentation. It does
  not change cache key composition (ADR-0004) or pipeline execution semantics.
- **Constraints.** Preserve deterministic stage behavior, stable cache keys, and the existing
  DiskCache on-disk JSON+NPZ format (ADR-0009). Avoid new default dependencies unless a backend is
  enabled.

### Options Considered

**Option A — Disk-only cache**
- **Description:** Keep `DiskCache` as the sole storage mechanism, with no backend abstraction.
- **Impact areas:** minimal code changes.
- **Pros:** simplest; zero new dependencies; fastest local I/O.
- **Cons:** no shared cache across machines; no backend choice for users.
- **Risks / Unknowns:** continued divergence in downstream forks for cloud caching.
- **Perf/Resource cost:** low latency on local disks; disk space usage.
- **Operational complexity:** low.
- **Security/Privacy/Compliance:** local filesystem only.
- **Dependencies / Externalities:** none.

**Option B — Pluggable cache backends (Disk + Redis)**
- **Description:** Introduce a cache backend interface and implement disk + Redis backends. Add
  timing metrics for lookup/store latency.
- **Impact areas:** `src/phys_pipeline/cache.py` (backend interface + disk impl), new Redis backend
  module, config types in `src/phys_pipeline/types.py` or new `cache_config.py`, updates in
  pipeline/stage caching hooks.
- **Pros:** supports local and shared caching; can capture perf metrics; extensible.
- **Cons:** additional API surface; optional Redis dependency; more tests.
- **Risks / Unknowns:** aligning artifact storage between disk and Redis; ensuring deterministic
  serialization across backends.
- **Perf/Resource cost:** disk is low-latency; Redis adds network RTT but enables cache reuse across
  workers.
- **Operational complexity:** moderate; requires Redis URL/creds for cloud usage.
- **Security/Privacy/Compliance:** Redis credentials management; potential for data retention
  policies.
- **Dependencies / Externalities:** Redis client (optional) and Redis service.

**Option C — External cache only (Redis/S3) with no disk**
- **Description:** Replace disk cache with a cloud-only cache.
- **Impact areas:** breaks local/offline workflows; removes ADR-0009 design.
- **Pros:** centralized cache for distributed runs.
- **Cons:** worsens developer experience; adds network dependency and cost.
- **Risks / Unknowns:** offline runs fail; increased operational load.
- **Perf/Resource cost:** higher latency due to network.
- **Operational complexity:** high.
- **Security/Privacy/Compliance:** strong reliance on cloud governance.
- **Dependencies / Externalities:** Redis/S3 required.

### Decision
- **Chosen option:** **Option B — Pluggable cache backends (Disk + Redis).**
- **Trade‑offs:** Accept a larger API surface and optional dependency to enable shared caching and
  performance diagnostics.
- **Scope of adoption:** Repository-level. Disk remains the default backend; Redis is opt-in.

### Actionable Implementation Plan (tied to current modules)
1. **Cache backend interface**
   - Add `CacheBackend` protocol and configuration object in `src/phys_pipeline/cache.py` (or new
     `cache_config.py`).
   - Keep `DiskCache` behavior unchanged and make it the default backend.
2. **Serialization utilities**
   - Add shared helpers in `src/phys_pipeline/cache.py` for serializing metadata + array payloads
     so disk and Redis store identical payload structures.
3. **Redis backend**
   - Implement `RedisCache` in a new module (e.g., `src/phys_pipeline/cache_redis.py`).
   - Use lazy import for the Redis client and surface a clear error when unavailable.
   - Support optional TTL via Redis `EXPIRE`.
4. **Pipeline/stage wiring**
   - Add backend selection hooks in pipeline/stage caching logic (where cache keys are computed).
   - Emit `cache_lookup_s` and `cache_store_s` in provenance or metrics.
5. **Tests**
   - Add unit tests for cache backend interface behavior.
   - Disk tests use temp dirs; Redis tests are integration-gated via env var.
6. **Docs**
   - Update `docs/how-to-build-simulations.md` with backend configuration and Redis URL examples.

### Consequences
- **Positive:** Enables shared cache across machines; supports local disk; exposes timing metrics for
  tuning; future backends can be added without redesign.
- **Negative / Mitigations:** Optional dependency management (use extras and lazy imports); ensure
  consistent serialization across backends with shared utilities.
- **Test strategy:**
  - Unit tests for backend interface behavior (get/put/miss semantics).
  - Disk backend tests use temp dirs.
  - Redis backend tests are optional/integration-gated via env var (documented in tests).
  - Timing metrics verified for presence (non-negative durations) without asserting absolute values.
- **Monitoring & Telemetry:**
  - Record `cache_lookup_s` and `cache_store_s` in provenance/metrics for each cached stage.
  - Optionally log backend name and cache hit/miss counts.
- **Documentation:**
  - Update cache usage docs (README or `docs/how-to-build-simulations.md`) with backend selection
    and Redis configuration examples.

### Alternatives Considered (but not chosen)
- Keep disk-only cache with no backend abstraction.
- External-only cache (Redis/S3) replacing disk cache.

### Open Questions
- How to store large artifacts in Redis (inline vs pointer to disk/object store)?
- Should cache timing be stored in `StageResult.metrics` vs `StageResult.provenance`?

### References
- `docs/adr/0004-cache-keys.md`
- `docs/adr/0009-disk-cache.md`
- `src/phys_pipeline/cache.py`

### Changelog
- `2026-02-07` — Proposed by @codex

---
