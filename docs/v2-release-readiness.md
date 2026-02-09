# V2 Release Readiness Checklist

Use this checklist before tagging a v2 release.

## Documentation
- [ ] Update README with DAG + scheduler overview.
- [ ] Confirm `docs/how-to-build-simulations.md` includes DAG examples.
- [ ] Ensure migration guide (`docs/v2-migration.md`) is current.
- [ ] Review ADRs for DAG execution and scheduler (ADR-0014/0015/0018).

## Testing
- [ ] Run offline-safe checks:
  ```bash
  python -m ruff check .
  python -m black --check .
  python -m mypy
  python -m pytest -q -m "not slow"
  ```
- [ ] Run slow tests if applicable:
  ```bash
  python -m pytest -q -m "slow"
  ```

## Benchmarks
- [ ] Run benchmarks:
  ```bash
  python scripts/benchmarks.py
  ```
- [ ] Record cache hit/miss results and scheduler overhead.

## Release metadata
- [ ] Update version in `pyproject.toml` and `src/phys_pipeline/__init__.py`.
- [ ] Draft release notes (features, breaking changes, migration pointers).
- [ ] Confirm CI green and artifacts published.
