# AGENTS

## Scope
This file applies to the entire repository unless a more specific `AGENTS.md` is added in a subdirectory.

## Repo overview
`phys-pipeline` provides a typed, sequential physics simulation pipeline with stages, caching, provenance, and optional artifact recording. The ADRs in `docs/adr/` capture architectural decisions; review them before making structural changes.

## Key references
- `docs/how-to-build-simulations.md` for end‑to‑end usage.
- `docs/issue-templates-guide.md` for issue/PR/ADR conventions.
- `docs/adr/` for architecture decisions and templates.
- `.github/pull_request_template.md` for PR content.

## Development conventions
- Prefer sequential pipeline semantics unless an ADR explicitly enables DAG execution.
- Stage outputs must follow the `StageResult` contract (scalar metrics, artifacts optional, deterministic `process`).
- Configs are frozen Pydantic models (`StageConfig`).
- Cache keys are based on state/config/policy; keep hashing stable.
- Use the ADR templates for architectural changes. Create new ADRs with:
  ```bash
  python scripts/adr_tools.py new "Title" --type full
  ```
  Then reindex:
  ```bash
  python scripts/adr_tools.py reindex
  ```

## Contribution expectations
- Keep iterating on changes until CI is green. If CI fails, fix the failures and update the branch.
- Add or update tests for any code you change (even if not explicitly requested).
- Update documentation whenever code changes affect existing docs or usage.

## Environment setup (required)
This repo uses a `src/` layout. Always install in editable mode with dev extras before running any checks:
```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

## Testing & checks
CI runs these checks; mirror them when feasible:
- Lint/hooks: `pre-commit run --all-files --show-diff-on-failure`
- Typecheck: `mypy`
- Fast tests: `pytest -q -m "not slow"`
- Slow tests (nightly): `pytest -q -m "slow"`

## Repo map
- Pipeline orchestration: `src/phys_pipeline/pipeline.py`
- Core types/contracts: `src/phys_pipeline/types.py`
- Caching + hashing: `src/phys_pipeline/cache.py`, `src/phys_pipeline/hashing.py`
- Artifact recording: `src/phys_pipeline/record.py`
- Error taxonomy: `src/phys_pipeline/errors.py`
- Tests: `tests/`

## Environment variables & secrets
- No repository-scoped secrets are required for local unit tests.
- If you add integration tests that require secrets, document them here and gate the tests accordingly.

## Pull request conventions
- Title format: `[phys-pipeline] <Title>`.

## Documentation updates
- Update README/docs/ADR references when public APIs or behavior change.
- Keep `docs/adr/INDEX.md` in sync with ADR additions/removals.
