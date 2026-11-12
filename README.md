# cuplyr-material

Benchmarks, results and social-media material for [cuplyr](https://github.com/bbtheo/cuplyr),
the GPU-backed dplyr API for R. The package itself lives in its own repository; this project
holds what is written about it.

## Layout

```
benchmarks/
  parquet-pipeline/   Parquet to summary: cuplyr vs DuckDB, dplyr and data.table
    harness/            the Quarto report source and the scripts that ran the measurements
    *.csv               raw measurements (timings.csv is the main one) and run provenance
    parquet-pipeline.html   the rendered report (self-contained)
    round-1/, round-2/  earlier report rounds, kept for the record
  rolling/            rolling-window benchmark redone with cuplyr (1e6 rows)
  rolling-1e7/        the same at 1e7 rows
  report-src/         template and build script for the rolling report
social/
  parquet-to-summary/ the four post images, plus build/ with the scripts that make them
```

Not tracked (see `.gitignore`): the generated parquet files (`parquet-pipeline/data/`, 4.6 GB),
the private R library `benchmarks/rlib/` (1.3 GB) and render caches.

## Where the code is

The measurement driver is part of the cuplyr repository, not this one:
`bench/parquet-pipeline.R`, `bench/parquet-lib.R` and `bench/rolling-*.R` (branch `dev`).
The harness here assumes a cuplyr checkout at `/home/theo/cuplr` and runs R through its
`tools/r` wrapper, which holds the GPU lock. Paths in the scripts are absolute.

## Reproducing the post images

```sh
python3 -I social/parquet-to-summary/build/make.py
```

This needs `rsvg-convert` and reads `benchmarks/parquet-pipeline/timings.csv` plus
`social/parquet-to-summary/build/split2.csv`. The two CSVs in `build/` come from
`split2.R` (read versus compute for dplyr and data.table at 1e8 rows) and `dt_threads.R`
(data.table thread scaling). Run those through `tools/r` in the cuplyr checkout.

## Measurement setup

All numbers come from one machine: i9-12900K (24 logical CPUs), 31 GB RAM, RTX 5070 with 12 GB.
Warm file cache, medians over quiet runs. The report in
`benchmarks/parquet-pipeline/parquet-pipeline.html` has versions, method and caveats.

## Licence

Apache-2.0, as cuplyr. See `LICENSE.md`.
