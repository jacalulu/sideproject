"""heal.py IN OUT — find hairline seams (single-row discontinuities) and heal them:
equalise the tone across each one with a symmetric ramp, then soften the few rows around it."""
import sys
import numpy as np
from PIL import Image
def find_seams(a, thresh=2.6, min_gap=120):
    d = np.abs(a[1:] - a[:-1]).mean(axis=(1, 2))
    med = np.array([np.median(d[max(0, i - 40):i + 40]) for i in range(len(d))])
    r = d / np.maximum(med, 0.5)
    rows = []
    for i in np.argsort(-r):
        if r[i] < thresh: break
        if all(abs(i + 1 - k) > min_gap for k, _ in rows): rows.append((i + 1, round(float(r[i]), 1)))
    return sorted(rows)
def heal(a, k, ramp=160, probe=30, soft=10):
    off = a[k - probe:k].mean(axis=(0, 1)) - a[k:k + probe].mean(axis=(0, 1))   # above minus below
    n = min(ramp, k, a.shape[0] - k)
    w = (1 - np.arange(n) / n)[:, None, None] ** 1.5
    a[k:k + n] += 0.5 * off * w                     # lift/lower below...
    a[k - n:k] -= 0.5 * off * w[::-1]               # ...and meet it halfway from above
    lo, hi = k - 3 * soft, k + 3 * soft             # then soften the seam itself
    seg = a[lo:hi].copy(); ker = np.exp(-0.5 * (np.arange(-2 * soft, 2 * soft + 1) / (soft / 2)) ** 2); ker /= ker.sum()
    pad = np.pad(seg, ((len(ker) // 2, len(ker) // 2), (0, 0), (0, 0)), mode="edge")
    blur = sum(ker[i] * pad[i:i + seg.shape[0]] for i in range(len(ker)))
    wgt = np.exp(-0.5 * ((np.arange(lo, hi) - k) / (soft * 0.9)) ** 2)[:, None, None]
    a[lo:hi] = seg * (1 - wgt) + blur * wgt
if __name__ == "__main__":
    im = Image.open(sys.argv[1]).convert("RGB")
    a = np.asarray(im, float).copy()
    seams = find_seams(a); print("seams found:", seams)
    for k, _ in seams: heal(a, k)
    print("after:", find_seams(a))
    Image.fromarray(np.clip(a, 0, 255).astype("uint8")).save(sys.argv[2])
