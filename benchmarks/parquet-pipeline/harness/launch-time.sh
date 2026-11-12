#!/usr/bin/env bash
# Wait for the readers step to end, then run the 12 time pieces, the first-call step and the probes.
H=/home/theo/cuplyr-material/benchmarks/parquet-pipeline/harness
LOG=/home/theo/cuplr/scratchpad/parity/features/F121/runs/round-2/coder
until grep -q "end readers" "$LOG/pieces.log"; do sleep 5; done
sleep 20
args=()
for size in 1e6 1e7 1e8; do
  for tab in narrow wide; do
    for cache in warm cold; do
      args+=("time-$size-$tab-$cache" "list(steps = 'time', sizes = $size, tables = '$tab', caches = '$cache')")
    done
  done
done
args+=("first" "list(steps = 'first')" "probe" "list(steps = 'probe')")
exec "$H/run-pieces.sh" "${args[@]}"
