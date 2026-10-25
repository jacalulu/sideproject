#!/usr/bin/env python3
"""embed_assets.py HTML key=path [key=path ...] — add or replace images in the game's ASSETS object
(as base64 data URLs), and copy each file next to the other loose originals in public/mermaid-dots/assets/."""
import sys, json, base64, shutil, os, mimetypes
html, pairs = sys.argv[1], sys.argv[2:]
s = open(html).read()
i = s.index("const ASSETS = "); j = s.index("\n", i)
obj = json.loads(s[i + len("const ASSETS = "):j].rstrip().rstrip(";"))
assets_dir = os.path.join(os.path.dirname(os.path.abspath(html)), "assets")
for pr in pairs:
    key, path = pr.split("=", 1)
    mime = mimetypes.guess_type(path)[0] or "image/webp"
    obj[key] = f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()
    dest = os.path.join(assets_dir, os.path.basename(path))
    if os.path.abspath(path) != os.path.abspath(dest): shutil.copy(path, dest)
    print(f"{key:16s} {os.path.getsize(path)/1024:6.1f} KB  -> assets/{os.path.basename(path)}")
s = s[:i] + "const ASSETS = " + json.dumps(obj, separators=(",", ":")) + ";" + s[j:]
open(html, "w").write(s); print(f"{html}: {len(s)/1e6:.2f} MB")
