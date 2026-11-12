#!/usr/bin/env bash
# Run the F121 round-2 steps one piece per tools/r call, logging the machine's
# state before each piece. Usage: run-pieces.sh <name> <PP list> [<name> <PP list> ...]
# Each pair is one tools/r call: PP is set to the given R list and the driver sourced.
# A pause between calls lets other worktrees take the GPU lock.
WT=/home/theo/cuplr-wt/F121
LOG=/home/theo/cuplr/scratchpad/parity/features/F121/runs/round-2/coder
STATS=/home/theo/cuplr/.git/cuplyr-locks/stats.tsv
while [[ $# -ge 2 ]]; do
  name="$1"; pp="$2"; shift 2
  {
    echo "== $name  $(date -Is)"
    uptime
    top -bn1 | head -15
    tail -6 "$STATS"
  } > "$LOG/quiet-before-$name.txt" 2>&1
  echo "$(date -Is) start $name" >> "$LOG/pieces.log"
  "$WT/tools/r" "PP <- $pp; source('bench/parquet-pipeline.R')" > "$LOG/$name.log" 2>&1
  rc=$?
  echo "$(date -Is) end $name rc=$rc" >> "$LOG/pieces.log"
  if [[ $rc -ne 0 ]]; then echo "$(date -Is) STOP after failure of $name" >> "$LOG/pieces.log"; exit $rc; fi
  sleep 20
done
