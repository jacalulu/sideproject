#!/usr/bin/env python3
"""strip.py STEP...  — build the continuous background strip by outpainting.
Step 0 paints the opening 9:16 panel. Every later step feeds the bottom OV rows of the
strip so far back to the model as the top of a new canvas, asks it to paint the rest,
then pastes the ORIGINAL pixels back over the top (feathered) so the join is exact."""
import sys, os, io, json, base64, urllib.request
from PIL import Image, ImageFilter
D = os.path.dirname(os.path.abspath(__file__))
S = os.environ.get("JOURNEY_WORK", os.path.join(os.getcwd(), "journey-work"))   # scratch output: strip/raw_*.png, strip/strip.png
os.makedirs(S + "/strip", exist_ok=True)
REF = D + "/refs/"           # the original eight zone paintings (style anchors for the opening panel)
MODEL = os.environ.get("JMODEL", "openai/gpt-5.4-image-2")   # held joins far better than gemini-3-pro-image in chapter 1
W, PH = 780, 1387                 # panel size (9:16 at 780 wide)
OV = 420                          # overlap rows shown to the model (30%)
KEEP = 760                        # of the fresh rows, keep only this many: the model paints seabed/ledges near the bottom of a panel
NEW = KEEP                        # fresh rows per step
FEATHER = 70
STYLE = ("Painterly, soft, luminous children's-storybook underwater art with gentle bioluminescent sparkles and "
         "soft god-rays, matching the style of the reference paintings. Tall vertical background for a children's mermaid "
         "puzzle game: detail and framing on the LEFT and RIGHT edges (reef walls, plants, rock), while the CENTER stays "
         "open, calm, low-contrast water so a game board can sit on it. No characters, no people, no text, no logos, "
         "no borders or frames, no hard horizontal lines.")
ZONES = json.load(open(D + "/zones.json"))
sys.path.insert(0, D)
from grade import grade_tail

ZONE_REF = ["bg-sunny-lagoon", "bg-coral-cove", "bg-kelp-forest", "bg-shipwreck-bay", "bg-pearl-palace",
            "bg-jellyfish-grove", "bg-twilight-deep", "bg-starlight-trench"]
PAL = json.load(open(D + "/palettes.json"))
def palette_text(y):
    z = min(7, int(y // 3575)); frac = (y % 3575) / 3575
    c = PAL[z]
    t = f" COLOUR PALETTE for this stretch: overall water colour {c['mid']}, deep shadows {c['dark']}, brightest glints {c['light']}."
    if frac > 0.72 and z < 7:
        n = PAL[z + 1]
        t += f" Over this panel the colours should begin sliding toward the next stretch's palette (water {n['mid']}, shadows {n['dark']}, glints {n['light']}), reaching it gradually, not abruptly."
    return t

def b64(im):
    buf = io.BytesIO(); im.convert("RGB").save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def call(prompt, imgs):
    content = [{"type": "text", "text": prompt}] + [{"type": "image_url", "image_url": {"url": b64(i)}} for i in imgs]
    body = {"model": MODEL, "messages": [{"role": "user", "content": content}],
            "modalities": ["image", "text"], "image_config": {"aspect_ratio": "9:16"}}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", json.dumps(body).encode(),
        {"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"], "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=400))
    m = r["choices"][0]["message"]
    if not m.get("images"): raise SystemExit("NO IMAGE " + json.dumps(r)[:600])
    out = Image.open(io.BytesIO(base64.b64decode(m["images"][0]["image_url"]["url"].split(",", 1)[1]))).convert("RGB")
    print("  model returned", out.size, "cost", r.get("usage", {}).get("cost"))
    return out.resize((W, PH), Image.LANCZOS)

def scene(y):
    # y = middle of the rows about to be painted. (25 levels = 2.5 screens = 3575px per zone)
    z = int(y // 3575); frac = (y % 3575) / 3575
    cur = ZONES[min(z, 7)]
    txt = f"SCENE: {cur['name']} — {cur['desc']}"
    if frac > 0.72 and z < 7: txt += f" The scene is GRADUALLY becoming {ZONES[z+1]['name']} ({ZONES[z+1]['desc']}) — blend the palettes smoothly, no sudden change."
    if frac < 0.28 and z > 0: txt += f" It has just gradually emerged from {ZONES[z-1]['name']}; keep a soft memory of that palette."
    if y > 26800: txt += (" THE FINAL STRETCH: the trench opens into a magnificent glowing royal sea-court. On one side a carved pearl-and-crystal "
                          "throne alcove lit with warm golden light, with glowing starry coral arches framing the edges.")
    if y > 27900: txt += (" THIS IS THE VERY END of the scroll: at the bottom centre a big luminous swirling whirlpool portal of cyan, violet and pink light "
                          "with sparkles spiralling into it, surrounded by glowing coral. The bottom edge may close here.")
    return txt + f""

LIGHT = (" Lighting: soft, diffuse, ambient glow only. Any light shafts are faint, wide and pass through the top edge as a continuation of the existing "
         "painting; NEVER draw the water surface, sun, or a fresh burst of rays beginning at the top edge. NEVER draw a seabed or floor.")

def strip_path(): return S + "/strip/strip.png"

def run(step):
    refs = [Image.open(REF + n).convert("RGB") for n in ("bg-sunny-lagoon.webp", "bg-coral-cove.webp")]
    if step == 0:
        p = (STYLE + " " + scene(PH / 2) + " This is the VERY TOP of the journey: the sunlit water surface with golden light rays "
             "is at the top edge. The reference images show the target art style only.")
        new = call(p, refs); new.save(S + f"/strip/raw_{step:02d}.png"); new.save(strip_path()); return
    cur = Image.open(strip_path()).convert("RGB")
    ctx = cur.crop((0, cur.height - OV, W, cur.height))
    # lower part = a blurry smear of the context's own bottom edge (continues colour + brightness, no flat-gray brightness cue)
    smear = ctx.crop((0, OV - 60, W, OV)).resize((W, PH - OV), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
    canvas = Image.new("RGB", (W, PH)); canvas.paste(smear, (0, OV)); canvas.paste(ctx, (0, 0))
    # fade the sharp context into the smear over its last FADE rows so the model sees no abrupt line to carry through
    FADE = 140
    soft = ctx.crop((0, OV - FADE, W, OV)).filter(ImageFilter.GaussianBlur(22))
    canvas.paste(soft, (0, OV - FADE), Image.linear_gradient("L").resize((W, FADE)))
    ymid = cur.height + KEEP / 2
    refs = []
    p = (STYLE + " " + scene(ymid) + palette_text(ymid) + LIGHT + f"\n\nThe FIRST image is a canvas whose TOP {int(OV/PH*100)}% is an existing painting and whose remaining "
         "lower part is only a blurry colour smear of the painting's bottom edge. Repaint that smeared area in full painted detail so it continues the painting seamlessly downward: same style, same lighting, "
         "same scale, edge structures (reef walls, plants) continuing naturally, the top part left exactly as it is. "
         "This is a slice from the MIDDLE of an extremely long vertical scroll that keeps descending, so it is NOT a complete picture: "
         "do NOT paint a water surface, a new burst of light rays from the top edge (only let the existing rays continue and fade), "
         "or any seabed, sand, floor, ledge, shelf or flat ground anywhere, and especially not at the bottom. The side walls keep running down past the bottom edge and the bottom edge is "
         "open water, because the scroll continues below. "
         "Output the full completed tall image.")
    best = None
    for attempt in range(1, int(os.environ.get("JTRIES", "4")) + 1):
        new = call(p, [canvas] + refs)
        new.save(S + f"/strip/raw_{step:02d}.png")
        res = new.copy(); res.paste(ctx, (0, 0))
        a = new.crop((0, OV - FEATHER, W, OV)); b = ctx.crop((0, OV - FEATHER, W, OV))
        mask = Image.linear_gradient("L").resize((W, FEATHER))          # 0 (top) -> 255 (bottom)
        res.paste(Image.composite(a, b, mask), (0, OV - FEATHER))
        out = Image.new("RGB", (W, cur.height + KEEP)); out.paste(cur, (0, 0))
        out.paste(res.crop((0, 0, W, OV + KEEP)), (0, cur.height - OV))
        out = tone_fix(out, cur.height)
        edge, bright, colour = seam_report(out, cur.height)
        ok = edge <= 3.0 and bright <= 9 and colour <= 14
        print(f"  attempt {attempt}: seam edge={edge} bright={bright} colour={colour} -> {'ok' if ok else 'BAD'}", flush=True)
        key = edge / 3.0 + bright / 9 + colour / 14
        if best is None or key < best[0]: best = (key, out)
        if ok: break
    final = grade_tail(best[1], cur.height - 100)   # keep the painting on its zone's intended brightness (models drift dark)
    final.save(strip_path()); print("  strip height", final.height, flush=True)

def tone_fix(im, j, ramp=350, probe=40):
    """match the new paint's overall tone to the existing painting at the join, fading the correction out over `ramp` rows"""
    import numpy as np
    arr = np.asarray(im, float)
    off = arr[j - probe:j].mean(axis=(0, 1)) - arr[j:j + probe].mean(axis=(0, 1))
    n = min(ramp, arr.shape[0] - j)
    arr[j:j + n] += off[None, None, :] * ((1 - np.arange(n) / ramp)[:, None, None] ** 1.5)
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))

def seam_report(im, j):
    """worst row-to-row discontinuity in the join zone + brightness/colour step across it"""
    import numpy as np
    a = np.asarray(im.crop((0, j - FEATHER - 60, W, j + 80)).convert("RGB"), float)
    d = np.abs(a[1:] - a[:-1]).mean(axis=(1, 2))
    med = np.array([np.median(d[max(0, i - 30):i + 30]) for i in range(len(d))])
    edge = float((d / np.maximum(med, 0.5)).max())
    k = FEATHER + 60
    above = a[k - 30:k - 2].mean(axis=(0, 1)); below = a[k + 2:k + 30].mean(axis=(0, 1))
    return round(edge, 1), round(float(abs(above.mean() - below.mean())), 1), round(float(np.abs(above - below).max()), 1)

if __name__ == "__main__":
    for a in sys.argv[1:]:
        if a.startswith("trim:"):
            im = Image.open(strip_path()); n = int(a[5:]); im.crop((0, 0, W, n)).save(strip_path()); print("trimmed to", n)
        elif a.startswith("seed"):
            Image.open(S + "/strip/raw_00.png").resize((W, PH), Image.LANCZOS).save(strip_path()); print("seeded from raw_00")
        elif a == "auto":
            n = 3
            while Image.open(strip_path()).height < 28600:
                print("step", n, flush=True); run(n); n += 1
        else:
            print("step", a); run(int(a))
