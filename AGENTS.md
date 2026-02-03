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

## Documentation updates
- Update README/docs/ADR references when public APIs or behavior change.
- Keep `docs/adr/INDEX.md` in sync with ADR additions/removals.

## Notes for wrapper repositories
If this repo is embedded or wrapped inside another repository, add an `AGENTS.md` in the wrapper’s root to describe:
- How the wrapper consumes or extends `phys-pipeline` (submodule, vendored copy, dependency).
- Any additional build/test commands specific to the wrapper.
- Integration constraints (e.g., supported Python versions, extra CI steps).
You generally do **not** need a separate `AGENTS.md` inside this repo unless wrapper‑specific instructions differ from the base repo or apply to only a subdirectory.
