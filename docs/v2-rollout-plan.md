# v2 Rollout Plan: DAG + Cache + Scheduler (ML + HPC)

This plan breaks each phase into **actionable steps**. Every feature increment explicitly
requires:

- **Tests** (unit + integration where relevant)
- **Documentation updates**
- **CI green** before moving to the next feature

> **Status:** Implemented across the codebase (see `docs/v2-migration.md` and
> `docs/v2-release-readiness.md` for follow-up guidance).

## Phase 1 — Foundations (DAG model + cache keying)

### Feature 1.1: DAG data model and validation
1. Define `PipelineGraph` data model and public API surface.
2. Implement DAG validation: cycle detection, dependency integrity checks.
3. Implement topological ordering and deterministic node traversal.
4. Add error taxonomy for DAG validation failures.
5. Add unit tests for DAG validation and topological ordering.
6. Update docs to describe DAG concept + API surface.
7. Run offline-safe checks and ensure CI green before proceeding.

### Feature 1.2: DAG-aware execution skeleton (single-threaded)
1. Implement DAG executor that runs nodes in topological order.
2. Wire execution to existing `Stage`/`StageResult` contracts.
3. Add provenance recording for node execution order and timestamps.
4. Add unit tests for ordered execution and provenance tracking.
5. Update docs with execution behavior + examples.
6. Run offline-safe checks and ensure CI green before proceeding.

### Feature 1.3: Cache keying v2 (DAG-aware)
1. Define cache key schema for DAG nodes (inputs + config + dependencies).
2. Implement stable hashing for DAG nodes and dependency outputs.
3. Add cache policy versioning to avoid invalid collisions.
4. Add tests for hash stability and cache hit/miss correctness.
5. Update docs to describe cache key schema + migration notes.
6. Run offline-safe checks and ensure CI green before proceeding.

## Phase 2 — Local Scheduler (parallel execution + resource slots)

### Feature 2.1: Scheduler abstraction
1. Define `Scheduler` interface with submit/status/result hooks.
2. Add a scheduler adapter layer to the DAG executor.
3. Add unit tests for scheduler lifecycle handling.
4. Update docs describing scheduler API and lifecycle.
5. Run offline-safe checks and ensure CI green before proceeding.

### Feature 2.2: Local scheduler (CPU/GPU slots)
1. Implement `LocalScheduler` with resource slot management.
2. Support basic concurrency (thread/process pool).
3. Enforce resource constraints per node.
4. Add tests for parallel execution ordering and resource limits.
5. Update docs with local scheduler usage examples.
6. Run offline-safe checks and ensure CI green before proceeding.

### Feature 2.3: Retry/timeout policy
1. Implement retry + timeout policy in DAG executor/scheduler.
2. Record retries and failure provenance.
3. Add tests for retry/backoff and timeout behavior.
4. Update docs describing failure handling policies.
5. Run offline-safe checks and ensure CI green before proceeding.

## Phase 3 — ML Scheduler Adapter

### Feature 3.1: GPU-aware scheduling policies
1. Add GPU resource requirements to node metadata.
2. Implement scheduler policy for GPU allocation.
3. Add tests for GPU constraint enforcement.
4. Update docs with GPU scheduling configuration.
5. Run offline-safe checks and ensure CI green before proceeding.

### Feature 3.2: Parameter sweep orchestration
1. Define sweep configuration schema and API.
2. Implement sweep expansion into DAG nodes.
3. Add tests for sweep expansion determinism and caching.
4. Update docs with sweep examples and usage guidance.
5. Run offline-safe checks and ensure CI green before proceeding.

### Feature 3.3: ML artifact packaging
1. Implement model artifact packaging hooks.
2. Add provenance metadata for model training stages.
3. Add tests for artifact capture and metadata integrity.
4. Update docs with artifact packaging conventions.
5. Run offline-safe checks and ensure CI green before proceeding.

## Phase 4 — HPC Scheduler Adapter

### Feature 4.1: HPC scheduler abstraction + adapters
1. Add scheduler adapter interfaces for Slurm/PBS (or pluggable API).
2. Implement job submission and polling.
3. Add tests with a mock HPC scheduler.
4. Update docs with HPC scheduler configuration details.
5. Run offline-safe checks and ensure CI green before proceeding.

### Feature 4.2: Shared filesystem cache support
1. Add shared cache store implementation (FS-based).
2. Implement consistency controls for multi-node access.
3. Add tests for concurrent cache access.
4. Update docs describing shared cache setup.
5. Run offline-safe checks and ensure CI green before proceeding.

### Feature 4.3: MPI / multi-node stage support
1. Add node metadata for MPI requirements.
2. Implement external runner hooks for MPI stages.
3. Add tests for MPI stage wiring (mock execution).
4. Update docs with MPI usage guidance and limitations.
5. Run offline-safe checks and ensure CI green before proceeding.

## Phase 5 — Hardening, Docs, and Migration

### Feature 5.1: Integration testing + benchmarks
1. Add integration tests for end-to-end DAG workflows.
2. Add benchmark suite for cache hit/miss and scheduler overhead.
3. Update docs with benchmark and performance notes.
4. Run offline-safe checks and ensure CI green before proceeding.

### Feature 5.2: Migration guidance + deprecations
1. Write migration guide for v1 → v2.
2. Document deprecations and compatibility notes.
3. Add tests verifying v1 pipeline compatibility.
4. Run offline-safe checks and ensure CI green before proceeding.

### Feature 5.3: Release readiness checklist
1. Validate docs (how-to, API docs, ADRs).
2. Ensure CI green with full test suite.
3. Create release notes and versioning strategy.
4. Sign off on rollout readiness.
