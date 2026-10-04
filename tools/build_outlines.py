"""Build content/outlines.json for the self-drawn SVG maps (no map API, no tiles).

Sources (public domain, Natural Earth, https://www.naturalearthdata.com):
- ne_10m_admin_0_countries_nep: country outlines as depicted by Nepal (point-of-view edition),
  so Nepal's outline follows its official map.
- ne_10m_rivers_lake_centerlines: the big Himalayan rivers (Karnali, Gandaki, Koshi systems).

Usage: python tools/build_outlines.py   (downloads into .cache/ on first run)
"""
import json
import math
import sys
import urllib.request
from pathlib import Path

sys.setrecursionlimit(100000)
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
FILES = {"countries": "ne_10m_admin_0_countries_nep.geojson", "rivers": "ne_10m_rivers_lake_centerlines.geojson"}
COUNTRIES = ["Nepal", "India", "China", "Bhutan", "Bangladesh"]
BOX = (79.0, 25.4, 89.6, 31.6)  # lng/lat window we ever draw


def fetch(name):
    CACHE.mkdir(exist_ok=True)
    p = CACHE / name
    if not p.exists():
        print("downloading", name)
        urllib.request.urlretrieve(BASE + name, p)
    return json.loads(p.read_text(encoding="utf-8"))


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        x0, y0 = pts[i]
        d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / norm
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return rdp(pts[: idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]


def clip_ok(xs, ys):
    return not (max(xs) < BOX[0] or min(xs) > BOX[2] or max(ys) < BOX[1] or min(ys) > BOX[3])


def rings(geom, eps, min_pts=4):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    out = []
    for poly in polys:
        ring = poly[0]
        if not clip_ok([p[0] for p in ring], [p[1] for p in ring]):
            continue
        pts = [(round(x, 3), round(y, 3)) for x, y in ring]
        mid = len(pts) // 2
        simp = rdp(pts[: mid + 1], eps)[:-1] + rdp(pts[mid:], eps)
        if len(simp) >= min_pts:
            out.append(simp)
    return out


def lines(geom, eps):
    parts = geom["coordinates"] if geom["type"] == "MultiLineString" else [geom["coordinates"]]
    out = []
    for ln in parts:
        pts = [(round(x, 3), round(y, 3)) for x, y in ln if BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3]]
        if len(pts) >= 2:
            out.append(rdp(pts, eps))
    return out


def main():
    countries = fetch(FILES["countries"])
    rivers = fetch(FILES["rivers"])
    out = {"countries": {}, "rivers": {}}
    for f in countries["features"]:
        name = f["properties"].get("ADMIN")
        if name in COUNTRIES:
            out["countries"][name] = rings(f["geometry"], 0.006 if name == "Nepal" else 0.03)
    for f in rivers["features"]:
        p = f["properties"]
        name = p.get("name") or ""
        if not f.get("geometry") or p.get("featurecla") != "River":
            continue
        ls = lines(f["geometry"], 0.01)
        if ls:
            out["rivers"].setdefault(name, []).extend(ls)
    dest = ROOT / "content" / "outlines.json"
    dest.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {dest} · countries {list(out['countries'])} · rivers {sorted(out['rivers'])} · "
          f"{dest.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
