# Sticker sheets (board pieces, map scenery, cast)

All art in the game's flat style comes from illustrated *sheets*: one image-model
call draws several pieces on a flat magenta background, then `slice.py` keys the
magenta out and cuts each piece into its own transparent PNG. The style guide
(linked in `DESIGN.md`) sets the rules; these scripts only make the pixels.
Needs `OPENROUTER_API_KEY`. About $0.14 per sheet with `google/gemini-3-pro-image`.

```
export STICKER_WORK=/some/scratch/dir
python3 -I tools/stickers/gen.py Z9 "<prompt>" style-ref.png     # -> $STICKER_WORK/out/Z9.png
cd $STICKER_WORK && python3 -I /path/to/tools/stickers/slice.py Z9   # -> spr/Z9/NN.png + spr/Z9_contact.png
```

Then label each sprite (place: edge / floor / water; motion: swim, bob, sway,
scuttle, rise, drift, pulse, none), export ≤256 px webp, embed with
`tools/embed_assets.py`, and add a row to `MAP_STICKERS` in `index.html`.

Lessons from the first run (Nov 2026):

- **Never say "sticker" in the prompt.** The model adds white sticker borders
  and outlines. Say "sprite sheet", and spell out "no white border, no outlines".
- **Pick the style reference carefully.** A game-screen mockup as image 1
  made the model redraw the whole screen six times out of six. Use a sheet of
  pieces on magenta (e.g. the friends sheet) as the reference instead.
- **Ask for faces only on animals.** Otherwise corals and rocks get faces.
- **Magenta background, no magenta in the art.** Keying is
  `min(R,B) - G`; pink pieces are fine, true magenta is not.
- **Expect leftovers.** One sheet drew an extra board and a duplicate crate;
  `slice.py` can crop a region first (see the SPECIALS case), and a 1 px alpha
  erosion plus a pink-pixel sweep cleans magenta fringes on square edges.
