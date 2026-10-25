import json, os
import numpy as np
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
PAL = json.load(open(D + "/palettes.json")); LUM = [p["lum"] for p in PAL]
ZONE_PX = 3575
def gauss1d(a, sigma):
    r = int(sigma * 3); k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2); k /= k.sum()
    pad = np.pad(a, (r, r), mode="edge"); return np.convolve(pad, k, mode="valid")
def target_curve(H):
    """intended average luminance at every row: the original zone paintings' brightness at each zone's centre, smoothstep between"""
    ys = (np.arange(8) + 0.5) * ZONE_PX; y = np.arange(H, dtype=float)
    out = np.empty(H)
    for i in range(H):
        if y[i] <= ys[0]: out[i] = LUM[0]
        elif y[i] >= ys[-1]: out[i] = LUM[-1]
        else:
            k = int(np.searchsorted(ys, y[i]) - 1); t = (y[i] - ys[k]) / ZONE_PX; t = t * t * (3 - 2 * t)
            out[i] = LUM[k] + (LUM[k + 1] - LUM[k]) * t
    return out
def grade(im, gmin=0.62, gmax=1.2, strength=1.0):
    """smooth per-row gamma that pulls the painting's brightness toward the zone targets (a continuous curve: no seams)"""
    a = np.asarray(im.convert("RGB"), float); H = a.shape[0]
    lum = gauss1d(a.mean(axis=(1, 2)), 350)
    tgt = target_curve(H)
    g = np.log(np.clip(tgt, 8, 250) / 255) / np.log(np.clip(lum, 8, 250) / 255)
    g = np.clip(1 + (g - 1) * strength, gmin, gmax); g = gauss1d(g, 150)
    out = 255 * (a / 255) ** g[:, None, None]
    return Image.fromarray(np.clip(out, 0, 255).astype("uint8")), g
if __name__ == "__main__":
    import sys
    r, g = grade(Image.open(sys.argv[1])); r.save(sys.argv[2]); print("gamma range", g.min().round(2), g.max().round(2))


def grade_tail(im, start, ramp=150, gmin=0.62, gmax=1.25):
    """grade only rows >= start toward the zone targets (earlier rows are already graded); the correction eases in over `ramp` rows"""
    a = np.asarray(im.convert("RGB"), float); H = a.shape[0]
    lum = gauss1d(a.mean(axis=(1, 2)), 350)[start:]
    tgt = target_curve(H)[start:]
    g = np.log(np.clip(tgt, 8, 250) / 255) / np.log(np.clip(lum, 8, 250) / 255)
    g = gauss1d(np.clip(g, gmin, gmax), 120)
    w = np.clip(np.arange(len(g)) / ramp, 0, 1); g = 1 + (g - 1) * w
    out = a.copy(); out[start:] = 255 * (a[start:] / 255) ** g[:, None, None]
    return Image.fromarray(np.clip(out, 0, 255).astype("uint8"))
