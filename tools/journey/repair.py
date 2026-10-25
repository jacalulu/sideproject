"""repair.py STRIP OUT ROW — ask the image model to repaint a seam region seamlessly, then blend only its middle back in."""
import sys, os, io, json, base64, urllib.request
import numpy as np
from PIL import Image
W, PH = 780, 1387
src, out, k = sys.argv[1], sys.argv[2], int(sys.argv[3])
im = Image.open(src).convert("RGB"); y0 = k - PH // 2
crop = im.crop((0, y0, W, y0 + PH))
buf = io.BytesIO(); crop.save(buf, "PNG")
prompt = ("This is a slice of one seamless, continuous vertical underwater painting for a children's game. Across the middle there is an "
          "unwanted horizontal seam: a band where the brightness and haze change abruptly. Repaint the image as ONE seamless continuous "
          "painting with no horizontal band, line or brightness step anywhere. Keep everything else the same: composition, colours, "
          "lighting, the reef, coral or kelp walls on both sides, the glowing specks, the open calm centre. Same size, no text, no border.")
body = {"model": "openai/gpt-5.4-image-2", "modalities": ["image", "text"], "image_config": {"aspect_ratio": "9:16"},
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt},
                     {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}}]}]}
req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", json.dumps(body).encode(),
    {"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"], "Content-Type": "application/json"})
r = json.load(urllib.request.urlopen(req, timeout=400)); m = r["choices"][0]["message"]
if not m.get("images"): raise SystemExit("NO IMAGE " + json.dumps(r)[:400])
new = Image.open(io.BytesIO(base64.b64decode(m["images"][0]["image_url"]["url"].split(",", 1)[1]))).convert("RGB").resize((W, PH), Image.LANCZOS)
print("cost", r.get("usage", {}).get("cost"))
new.save(out + ".raw.png")
# blend: original at the crop's top/bottom, the repaint in the middle (+-330 rows), 220-row feathers between
a = np.asarray(im, float).copy(); c = np.asarray(crop, float); n = np.asarray(new, float)
y = np.arange(PH) - PH / 2
w = np.clip((330 + 220 - np.abs(y)) / 220, 0, 1)[:, None, None]
w = w * w * (3 - 2 * w)
a[y0:y0 + PH] = c * (1 - w) + n * w
Image.fromarray(np.clip(a, 0, 255).astype("uint8")).save(out)
