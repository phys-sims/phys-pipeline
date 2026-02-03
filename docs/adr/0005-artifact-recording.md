# ADR-0005: Artifact recording and storage formats

- Status: Proposed
- Date: 2026-02-03
- Deciders: @tbd
- Area: phys-pipeline
- Related: src/phys_pipeline/record.py, src/phys_pipeline/accumulator.py
- Tags: artifacts, logging

## Decision
- Artifacts are optional and recorded only when requested.
- Figures are saved as `.png`, blobs as `.json`.
- Large artifacts are previewed in results to avoid memory blowups.

## Consequences
- Pipeline results remain light by default
- Artifact paths are stored in output when recording is enabled
