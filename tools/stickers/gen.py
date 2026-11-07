# usage: STICKER_WORK=dir python3 -I gen.py NAME "prompt" ref1.png [ref2.png ...]  -> $STICKER_WORK/out/NAME.png (OpenRouter image model)
import base64, json, os, sys, urllib.request
name, prompt, refs = sys.argv[1], sys.argv[2], sys.argv[3:]
content = [{"type": "text", "text": prompt}]
for p in refs:
    content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()}})
body = {"model": os.environ.get("IMG_MODEL", "google/gemini-3-pro-image"), "modalities": ["image", "text"],
        "messages": [{"role": "user", "content": content}]}
req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
      headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"], "Content-Type": "application/json"})
r = json.load(urllib.request.urlopen(req, timeout=400))
imgs = r["choices"][0]["message"].get("images") or []
if not imgs: print(name, "NO IMAGE", str(r["choices"][0]["message"].get("content"))[:300]); sys.exit(1)
out = os.path.join(os.environ.get('STICKER_WORK', '.'), 'out', name + '.png'); os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "wb").write(base64.b64decode(imgs[0]["image_url"]["url"].split(",", 1)[1]))
print(name, "ok", r.get("usage", {}).get("cost"))
