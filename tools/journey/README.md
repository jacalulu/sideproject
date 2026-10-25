# Journey painting pipeline

Makes the one continuous background painting for a 200-level chapter
(780 x 28,600 px), then slices and embeds it in the game. Chapter 1 cost
about $10 of OpenRouter credit, roughly half of it on experiments that
built this pipeline; a fresh chapter should be closer to $5.
Needs `OPENROUTER_API_KEY`.

```
export JOURNEY_WORK=/some/scratch/dir      # outputs: $JOURNEY_WORK/strip/
python3 -I tools/journey/strip.py 0         # the opening panel (sunlit surface)
python3 -I tools/journey/strip.py trim:1000 # cut it above any seabed the model painted
python3 -I tools/journey/strip.py auto      # outpaint downward until >= 28,600 px
```

Then finish and embed:

```
# squash to exactly 28,600 rows (never crop: the finale sits at the very bottom)
python3 -I -c "from PIL import Image; Image.open('strip.png').resize((780,28600), Image.LANCZOS).save('final.png')"
python3 -I tools/journey/heal.py final.png healed.png        # soften hairline seams
python3 -I tools/journey/repair.py healed.png fixed.png ROW  # repaint one stubborn seam band
python3 -I tools/journey/embed.py fixed.png public/mermaid-dots/index.html public/mermaid-dots/index.html \
        --write-assets public/mermaid-dots/assets
```

## How a step works (and why)

Each step gives the model a 9:16 canvas: the TOP 420 rows are the bottom
of the painting so far; the rest is a blurred smear of that edge. The
model paints the smear, the ORIGINAL pixels are pasted back over the
overlap, and only the first 760 fresh rows are kept. Every rule below was
learned from a failure in chapter 1:

- **Smear, not flat gray, below the context.** Flat mid-gray acted as a
  brightness cue and the model painted a bright new scene under a dark one.
- **Fade the context into the smear** (last 140 rows). A sharp-to-blurry
  edge became a horizontal line the model carried through.
- **Keep only the first 760 new rows.** Models end every panel with a
  seabed or ledge, and continuing from a floor makes them start over.
- **No reference images after the opening panel.** Full paintings got
  their composition (and seabeds) copied; even blurred swatches were read
  as top-to-bottom layouts. Palettes go in as hex colours in the text.
- **Seam check + up to 4 retries per step** (`seam_report`): a row
  discontinuity ratio <= 3 and a small tone step across the join.
- **`tone_fix`** fades out any overall colour step at the join.
- **`grade_tail`** keeps each zone on its intended brightness
  (`palettes.json`, measured from the original zone paintings in
  `refs/`). Without it the strip drifted 40-50% too dark.
- **GPT-5.4 Image over Gemini 3 Pro Image**: on the same hard step Gemini
  failed 4 of 4 attempts; GPT passed with a cleaner join, and kept a much
  higher first-try pass rate after that.

`zones.json` holds each zone's scenery description; `strip.py` blends to
the next zone over the last 28% of each 3,575 px zone, and adds the
throne-room and whirlpool finale near the bottom.
