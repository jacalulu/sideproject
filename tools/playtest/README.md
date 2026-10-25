# Playtest bot

`bot.js` loads the real game in headless Chromium (Playwright) and plays it:
at every move it searches lines (depth 8, 500 nodes per starting cell) and
2x2 loops, scores each against the current goals (useful friends, sand on or
next to the line, crates/oysters beside it, cells under anchors, jelly
friends), and plays the best. Animations are skipped by settling the board
instantly, so all 200 levels take a few minutes.

It is a *comparison* tool, not a model of a child: it wins levels 1-25 about
70% of the time, which a real player finds easy. What matters is the gap
between a zone's mechanic levels and its breather levels (every 5th level
has no mechanic) - keep them within noise (about +-10% at 4 runs).

    RUNS=4 tools/playtest/sweep.sh && python3 tools/playtest/summary.py tools/playtest/out/sweep_all.jsonl
    UNL=1 RUNS=3 tools/playtest/sweep.sh     # waves actually needed per level

Each result row has `why` counts for unfinished runs: `cap` (ran past 80
moves) or `nomove` (no legal move - a real deadlock; must be zero).
