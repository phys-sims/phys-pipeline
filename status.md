# v2 Release Status

Last updated: 2026-02-11

## Completed in this update

- ✅ Bumped local package version to `2.0.0` in project metadata and runtime version export.
- ✅ Updated version assertion test to validate `2.0.0`.
- ✅ Added dedicated `v2.0.0` release notes.
- ✅ Updated README documentation index to include v2.0.0 release notes.
- ✅ Updated release-readiness checklist to reflect completed validation and benchmark capture.
- ✅ Ran v2 benchmark script and recorded outputs:
  - Cache benchmark: cold `0.0037s`, warm `0.0005s`.
  - Scheduler benchmark: `0.0112s`.

## v2 readiness snapshot

### Documentation
- [x] Update README with DAG + scheduler overview.
- [x] Confirm `docs/how-to-build-simulations.md` includes DAG examples.
- [x] Ensure migration guide (`docs/v2-migration.md`) is current.
- [x] Review ADRs for DAG execution and scheduler (ADR-0014/0015/0018).

### Testing
- [x] Validation narrative covering DAG validation, scheduler/provenance capture, cache hit/miss,
      sweep expansion, and model artifact packaging.
- [x] Run offline-safe checks (`ruff`, `black --check`, `mypy`, `pytest -m "not slow"`).
- [x] Run slow tests (`pytest -m "slow"`).

### Benchmarks
- [x] Run `python scripts/benchmarks.py`.
- [x] Record cache hit/miss results and scheduler overhead.

### Release metadata
- [x] Update version in `pyproject.toml` and `src/phys_pipeline/__init__.py`.
- [x] Draft release notes (features, breaking changes, migration pointers).
- [ ] Confirm CI green and artifacts published (requires remote pipeline run after push/tag).
