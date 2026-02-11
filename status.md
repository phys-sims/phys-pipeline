# v2 Release Status

Last updated: 2026-02-11

## Completed in this update

- ✅ Ran slow-test suite for release validation:
  - `python -m pytest -q -m "slow"`
  - Result: `1 passed, 46 deselected`
- ✅ Captured current release-readiness snapshot for v2.
- ✅ Audited v2 documentation coverage and confirmed required docs are current:
  - README contains DAG + scheduler overview.
  - `docs/how-to-build-simulations.md` includes DAG examples.
  - `docs/v2-migration.md` reflects current v1 → v2 guidance.
  - ADR index includes ADR-0014, ADR-0015, and ADR-0018 entries.

## v2 readiness snapshot

### Documentation
- [x] Update README with DAG + scheduler overview.
- [x] Confirm `docs/how-to-build-simulations.md` includes DAG examples.
- [x] Ensure migration guide (`docs/v2-migration.md`) is current.
- [x] Review ADRs for DAG execution and scheduler (ADR-0014/0015/0018).

### Testing
- [ ] Validation narrative covering DAG validation, scheduler/provenance capture, cache hit/miss,
      sweep expansion, and model artifact packaging.
- [ ] Run offline-safe checks (`ruff`, `black --check`, `mypy`, `pytest -m "not slow"`).
- [x] Run slow tests (`pytest -m "slow"`).

### Benchmarks
- [ ] Run `python scripts/benchmarks.py`.
- [ ] Record cache hit/miss results and scheduler overhead.

### Release metadata
- [ ] Update version in `pyproject.toml` and `src/phys_pipeline/__init__.py`.
- [ ] Draft release notes (features, breaking changes, migration pointers).
- [ ] Confirm CI green and artifacts published.
