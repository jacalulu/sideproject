#!/bin/bash
# Play every level 1-200 with the bot, 4 parallel chunks.
#   RUNS=4 tools/playtest/sweep.sh            -> win rates (compare with: python3 tools/playtest/summary.py OUT/sweep_all.jsonl)
#   UNL=1 RUNS=3 tools/playtest/sweep.sh      -> unlimited waves: records how many waves each level actually needs
set -e
D=$(cd "$(dirname "$0")" && pwd); H=${HTML:-$D/../../public/mermaid-dots/index.html}; OUT=${OUT:-$D/out}; mkdir -p "$OUT"
export NODE_PATH=${NODE_PATH:-$(npm root -g)}
for r in "1 50" "51 100" "101 150" "151 200"; do set -- $r; node "$D/bot.js" "$H" $1 $2 ${RUNS:-4} > "$OUT/chunk_$1.jsonl" 2>&1 & done; wait
cat "$OUT"/chunk_*.jsonl | grep '^{' > "$OUT/sweep_all.jsonl"; grep -h errors "$OUT"/chunk_*.jsonl
