**Title:** Redis cache backend implementation

- **ADR ID:** `ADR-0020`
- **Status:** `Proposed`
- **Date:** `2026-02-07`
- **Deciders:** `@phys-pipeline-maintainers`
- **Area:** `phys-pipeline`
- **Related:** `ADR-0004, ADR-0009, ADR-0019`
- **Tags:** `performance, api, ops, caching`
- **Scope:** `repo`
- **Visibility:** `public`
- **Canonical ADR:** `phys-pipeline/docs/adr/0020-redis-cache-backend.md`
- **Impacted repos:** `phys-pipeline`
- **Related ecosystem ADRs:** `N/A`

### Context
- **Problem statement.** Teams need a shared cache to reuse stage outputs across machines or CI
  workers, while preserving existing cache-key semantics and deterministic behavior.
- **In/Out of scope.** This ADR covers Redis as an optional cache backend. It does not change cache
  keys or stage semantics, and it does not require Redis for local-only workflows.
- **Constraints.** Keep `DiskCache` as the default (ADR-0009). Avoid adding mandatory dependencies
  for users who only need local caching.

### Decision
- **Chosen option:** Add an optional Redis backend behind a backend interface, selectable via cache
  configuration. Redis is opt-in and requires explicit configuration.

### Design Details
- **Backend interface:** Add a `CacheBackend` protocol in `src/phys_pipeline/cache.py` (or new
  `cache_backends.py`) with `get`, `put`, `exists` semantics aligned to existing DiskCache.
- **Data format:** Store metadata JSON and compressed array payloads. Use a stable serialization
  wrapper so disk and Redis store identical payload structures.
- **Keying:** Use the existing cache key contract (ADR-0004) without modification.
- **TTL:** Support optional TTL when using Redis (`EXPIRE`).
- **Timing instrumentation:** Record `cache_lookup_s` and `cache_store_s` in provenance/metrics (per
  ADR-0019).

### Actionable Implementation Steps
1. **Backend abstraction**
   - Introduce `CacheBackend` protocol and a `CacheConfig` model for selecting `disk` or `redis`.
   - Keep `DiskCache` API stable; wrap it in an adapter if needed.
2. **Serialization utilities**
   - Add shared helpers to serialize/deserialize `{meta, arrays}` to/from bytes.
3. **Redis backend**
   - Implement `RedisCache` with lazy import of the Redis client.
   - Store metadata under a `:meta` key and arrays under a `:arrays` key (or a single packed blob).
   - Implement TTL support.
4. **Pipeline/stage integration**
   - Add cache selection hooks where cache lookups are performed.
   - Emit timing metrics and backend metadata in provenance.
5. **Tests**
   - Unit tests for backend interface compliance and serialization correctness.
   - Redis tests gated by `PHYS_PIPELINE_REDIS_URL` or pytest marker `redis`.
6. **Docs**
   - Update `docs/how-to-build-simulations.md` with Redis configuration examples.

### Consequences
- **Positive:** Shared cache for distributed workloads; optional adoption.
- **Negative / Mitigations:** Additional optional dependency; gate Redis usage with extras and lazy
  imports to avoid forcing installs.

### References
- `docs/adr/0004-cache-keys.md`
- `docs/adr/0009-disk-cache.md`
- `docs/adr/0019-cache-backend-options-and-performance-instrumentation.md`

### Changelog
- `2026-02-07` — Proposed by @codex

---
