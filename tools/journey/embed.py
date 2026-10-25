#!/usr/bin/env python3
"""embed.py STRIP.png HTML_IN HTML_OUT [--write-assets DIR] [--q 70] [--test-pad]
Slices the journey strip into 20 x (780x1430) webp, embeds them as bgJ00..bgJ19 data URLs in the ASSETS
object of the game HTML (dropping the eight old bg* keys)."""
import sys, json, base64, io, argparse, re
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument("strip"); ap.add_argument("html_in"); ap.add_argument("html_out")
ap.add_argument("--write-assets"); ap.add_argument("--q", type=int, default=70); ap.add_argument("--test-pad", action="store_true")
a = ap.parse_args()
W, SH, N = 780, 1430, 20
st = Image.open(a.strip).convert("RGB")
if st.height < SH * N:
    if not a.test_pad: sys.exit(f"strip too short: {st.height} < {SH*N}")
    big = Image.new("RGB", (W, SH * N)); y = 0
    while y < SH * N: big.paste(st, (0, y)); y += st.height
    st = big
st = st.crop((0, 0, W, SH * N))
slices = {}
total = 0
for i in range(N):
    buf = io.BytesIO(); st.crop((0, i * SH, W, (i + 1) * SH)).save(buf, "WEBP", quality=a.q, method=6)
    slices[f"bgJ{i:02d}"] = buf.getvalue(); total += len(buf.getvalue())
    if a.write_assets: open(f"{a.write_assets}/journey-{i:02d}.webp", "wb").write(buf.getvalue())
print(f"{N} slices, {total/1e6:.2f} MB webp")
s = open(a.html_in).read()
i = s.index("const ASSETS = "); j = s.index("\n", i)
obj = json.loads(s[i + len("const ASSETS = "):j].rstrip().rstrip(";"))
for k in [k for k in obj if k.startswith("bg") and not re.fullmatch(r"bgJ\d\d", k)]: del obj[k]   # old zone paintings (note: "bgJelly" starts with "bgJ")
for k, v in slices.items(): obj[k] = "data:image/webp;base64," + base64.b64encode(v).decode()
s = s[:i] + "const ASSETS = " + json.dumps(obj, separators=(",", ":")) + ";" + s[j:]
open(a.html_out, "w").write(s); print("wrote", a.html_out, f"{len(s)/1e6:.2f} MB")
