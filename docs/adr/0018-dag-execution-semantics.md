**Title:** Define DAG execution semantics and dependency types

- **ADR ID:** `ADR-0018`
- **Status:** `Proposed`
- **Date:** `2026-02-04`
- **Deciders:** `@phys-pipeline-maintainers`
- **Area:** `phys-pipeline`
- **Related:** `ADR-0002, ADR-0003, ADR-0004, ADR-0008, ADR-0014, ADR-0015`
- **Tags:** `execution, dag, caching, contracts`
- **Scope:** `repo`
- **Visibility:** `public`
- **Canonical ADR:** `phys-pipeline/docs/adr/0018-dag-execution-semantics.md`

### Context
- **Problem statement.** DAG execution is planned (ADR-0014/0015), but we need a concise, explicit spec for node/dependency semantics, determinism, memoization, and compatibility with the sequential pipeline baseline (ADR-0002).
- **In/Out of scope.** In scope: node types, dependency types, determinism requirements, memoization scope, and compatibility rules. Out of scope: scheduler implementation details, parallel execution policies, and distributed execution.
- **Constraints.** Preserve deterministic debugging and stable cache keys (ADR-0003/0004). Keep behavior consistent with sequential pipelines and pipeline-as-stage composition (ADR-0002/0008).

### Options Considered
**Option A — Deterministic DAG with typed dependencies and sequential-compatible scheduling**
- **Description:** Nodes are stages (or pipeline-as-stage). Dependencies are explicitly typed (data, artifact, config). Scheduler defaults to deterministic topological execution compatible with existing sequential behavior.
- **Impact areas:** data model, public API, caching, docs
- **Pros:** clear semantics, stable memoization, easy back-compat, minimal surprises
- **Cons:** limits implicit parallelism; requires explicit dependency declaration
- **Risks / Unknowns:** modeling artifact/config dependencies in APIs
- **Perf/Resource cost:** minimal overhead for dependency resolution
- **Operational complexity:** low
- **Security/Privacy/Compliance:** none
- **Dependencies / Externalities:** none

**Option B — Implicit dependency inference with parallel-first scheduling**
- **Description:** infer dependencies from state/artifact access and prioritize parallel execution.
- **Impact areas:** data model, scheduler, caching
- **Pros:** less user wiring, potential speedups
- **Cons:** ambiguous semantics, harder determinism, brittle cache keys
- **Risks / Unknowns:** silent dependency mismatches, non-reproducible runs
- **Perf/Resource cost:** higher scheduler complexity
- **Operational complexity:** medium/high
- **Security/Privacy/Compliance:** none
- **Dependencies / Externalities:** likely third-party graph tooling

### Decision
- **Chosen option:** Option A, because it preserves the sequential baseline while explicitly enabling DAG representation and deterministic scheduling.
- **Trade‑offs:** we accept more explicit wiring in exchange for predictable execution and stable memoization.
- **Scope of adoption:** applies to DAG builder/scheduler APIs and any future executor; sequential pipelines remain the default path.

### Consequences
- **Positive:**
  - **Allowed node types:** nodes represent `PipelineStage` instances or a pipeline-as-stage wrapper (ADR-0008).
  - **Allowed dependency types:**
    - **Data dependency:** downstream consumes upstream `StageResult.state`.
    - **Artifact dependency:** downstream consumes upstream `StageResult.artifacts` or recorded artifacts.
    - **Config dependency:** downstream depends on upstream configuration or policy outputs that influence hashing.
  - **Determinism expectations:** `PipelineStage.process` remains deterministic and side-effect free (ADR-0003). Artifact outputs must be reproducible given identical inputs/config/policy.
  - **Memoization scope:** caching is per node, keyed by state/config/policy/version (ADR-0004). Cached results may be reused within a run and across runs (disk cache), but never across incompatible configs or policies.
  - **Backward compatibility:** the default scheduler must emulate sequential pipeline behavior when the DAG is a straight line; no implicit reordering beyond topological constraints, and pipeline-as-stage must behave identically to existing sequential composition.
- **Negative / Mitigations:** explicit dependency typing adds API surface; mitigate with builder helpers and validation errors (ADR-0014).
- **Migration plan:** none for current sequential pipelines; DAG APIs are additive.
- **Test strategy:** add contract tests for dependency typing and determinism invariants when DAG builder/scheduler land.
- **Monitoring & Telemetry:** log scheduler order and cache hits to verify determinism.
- **Documentation:** update DAG builder/scheduler docs when implementations are added.

### Alternatives Considered (but not chosen)
- Inferring dependencies from runtime access patterns (Option B).

### Open Questions
- How to represent config dependencies in `NodeSpec` (explicit list vs. policy bag reference).
- Whether artifact dependencies require stronger content-addressable hashing.

### References
- `docs/adr/0002-sequential-execution.md`
- `docs/adr/0003-stage-contract.md`
- `docs/adr/0004-cache-keys.md`
- `docs/adr/0008-pipeline-as-stage.md`
- `docs/adr/0014-dag-builder.md`
- `docs/adr/0015-dag-scheduler.md`

### Changelog
- `2026-02-04` — Proposed by @codex

---
