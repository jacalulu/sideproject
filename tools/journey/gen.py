#!/usr/bin/env python3
"""gen.py MODEL OUT.png PROMPT [--ref file ...] [--ar 1:1]  — image gen via OpenRouter."""
import sys, os, json, base64, urllib.request, argparse, mimetypes, io
from PIL import Image
ap = argparse.ArgumentParser()
ap.add_argument("model"); ap.add_argument("out"); ap.add_argument("prompt")
ap.add_argument("--ref", action="append", default=[]); ap.add_argument("--ar", default=None)
a = ap.parse_args()
content = [{"type": "text", "text": a.prompt}]
for r in a.ref:
    im = Image.open(r).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    buf = io.BytesIO(); bg.convert("RGB").save(buf, "PNG")
    content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}})
body = {"model": a.model, "messages": [{"role": "user", "content": content}], "modalities": ["image", "text"]}
if a.ar: body["image_config"] = {"aspect_ratio": a.ar}
req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", json.dumps(body).encode(),
    {"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"], "Content-Type": "application/json"})
resp = json.load(urllib.request.urlopen(req, timeout=300))
msg = resp["choices"][0]["message"]
imgs = msg.get("images") or []
if not imgs:
    print("NO IMAGE:", json.dumps(resp)[:800]); sys.exit(1)
url = imgs[0]["image_url"]["url"]
open(a.out, "wb").write(base64.b64decode(url.split(",", 1)[1]))
print("ok", a.out, Image.open(a.out).size, "usage:", resp.get("usage", {}).get("cost"))
