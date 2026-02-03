# ADR-0013: ADR process and indexing

- Status: Proposed
- Date: 2026-02-03
- Deciders: @tbd
- Area: infra/docs
- Related: scripts/adr_tools.py
- Tags: docs, process

## Decision
Create ADRs via `python scripts/adr_tools.py new "Title" --type full`
and reindex with `python scripts/adr_tools.py reindex`.

## Consequences
- Consistent naming and indexing
- Faster doc hygiene
