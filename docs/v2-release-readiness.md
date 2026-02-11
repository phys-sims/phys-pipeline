# V2 Release Readiness Checklist

Use this checklist before tagging a v2 release.

## Documentation
- [x] Update README with DAG + scheduler overview.
- [x] Confirm `docs/how-to-build-simulations.md` includes DAG examples.
- [x] Ensure migration guide (`docs/v2-migration.md`) is current.
- [x] Review ADRs for DAG execution and scheduler (ADR-0014/0015/0018).

## Testing
- [x] Validation narrative: confirm v2 execution correctness via DAG validation (duplicate/missing/cycle),
  scheduler/provenance capture (version + policy hash), cache hit/miss, sweep expansion, and
  model artifact packaging tests. Summarize the results in release notes or PR description.
- [x] Run offline-safe checks:
  ```bash
  python -m ruff check .
  python -m black --check .
  python -m mypy
  python -m pytest -q -m "not slow"
  ```
- [x] Run slow tests if applicable:
  ```bash
  python -m pytest -q -m "slow"
  ```

## Benchmarks
- [x] Run benchmarks:
  ```bash
  python scripts/benchmarks.py
  ```
- [x] Record cache hit/miss results and scheduler overhead.
  - Cache benchmark: cold `0.0037s`, warm `0.0005s`.
  - Scheduler benchmark: `0.0112s` for 8 jobs at 10ms each.

## Release metadata
- [x] Update version in `pyproject.toml` and `src/phys_pipeline/__init__.py`.
- [x] Draft release notes (features, breaking changes, migration pointers).
- [ ] Confirm CI green and artifacts published (requires remote CI run/artifact publication after push/tag).
