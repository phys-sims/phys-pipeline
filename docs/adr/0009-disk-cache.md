# ADR-0009: DiskCache format and lifecycle

- Status: Proposed
- Date: 2026-02-03
- Deciders: @tbd
- Area: phys-pipeline
- Related: src/phys_pipeline/cache.py
- Tags: caching, storage

## Decision
Cache values are stored as:
- Metadata JSON (`<key>.json`)
- Numpy arrays in compressed NPZ (`<key>.npz`)

## Consequences
- Cache is inspectable and portable
- Invalidations are explicit (delete files)
