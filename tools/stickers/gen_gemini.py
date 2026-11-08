# usage: [ASPECT=9:16] python3 -I gen_gemini.py NAME "prompt" ref1.png [ref2.png ...] -> out/NAME.png  (Gemini API, GEMINI_API_KEY)
import base64, json, os, sys, urllib.request, mimetypes
name, prompt, refs = sys.argv[1], sys.argv[2], sys.argv[3:]
parts = [{"text": prompt}]
for p in refs:
    parts.append({"inline_data": {"mime_type": mimetypes.guess_type(p)[0] or "image/png", "data": base64.b64encode(open(p, "rb").read()).decode()}})
cfg = {"responseModalities": ["IMAGE"]}
if os.environ.get("ASPECT"): cfg["imageConfig"] = {"aspectRatio": os.environ["ASPECT"]}
model = os.environ.get("IMG_MODEL", "gemini-3-pro-image")
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
      data=json.dumps({"contents": [{"parts": parts}], "generationConfig": cfg}).encode(),
      headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"})
try:
    r = json.load(urllib.request.urlopen(req, timeout=400))
except urllib.error.HTTPError as e:
    print(name, "HTTP", e.code, e.read()[:400]); sys.exit(1)
for part in r.get("candidates", [{}])[0].get("content", {}).get("parts", []):
    d = part.get("inlineData") or part.get("inline_data")
    if d:
        out = os.path.join(os.environ.get("STICKER_WORK", "."), "out", name + ".png"); os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "wb").write(base64.b64decode(d["data"])); print(name, "ok"); sys.exit(0)
print(name, "NO IMAGE", json.dumps(r)[:400]); sys.exit(1)
