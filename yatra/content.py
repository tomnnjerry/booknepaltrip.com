"""In-memory catalogue built from content/*.json.

Every page on the site is rendered from this catalogue. In DEBUG the catalogue
reloads when any content file changes, so writers see edits on refresh.
"""
import json
import math
import random
import re
from collections import OrderedDict
from pathlib import Path

from django.conf import settings
from django.urls import reverse

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MONTH_SHORT = [m[:3] for m in MONTHS]
# Nepal runs on Bikram Sambat. Each Gregorian month straddles two Nepali months (they turn mid-month).
BS_MONTHS = [("Poush", "पौष"), ("Magh", "माघ"), ("Falgun", "फागुन"), ("Chaitra", "चैत"), ("Baisakh", "वैशाख"),
             ("Jestha", "जेठ"), ("Asar", "असार"), ("Shrawan", "साउन"), ("Bhadra", "भदौ"), ("Asoj", "असोज"),
             ("Kartik", "कात्तिक"), ("Mangsir", "मंसिर")]
# January starts in Poush and turns to Magh around the 14th-15th, and so on round the year
BS_FOR_MONTH = [(BS_MONTHS[i], BS_MONTHS[(i + 1) % 12]) for i in range(12)]
DEVANAGARI_DIGITS = str.maketrans("0123456789", "०१२३४५६७८९")

REGION_ORDER = ["kathmandu-valley", "pokhara-annapurna", "everest-khumbu", "chitwan-terai", "lumbini",
                "mustang-dolpo", "langtang-manaslu", "eastern-nepal", "far-west"]

# Each region wears the colours it is known for.
# ground = dark sections, accent = highlights on dark, ink = accent text on paper, tint = light wash,
# grad = 3-stop dark ground, foil = metallic accent (light -> mid -> deep), icon = drawn emblem
LANDS = {
    "kathmandu-valley": {"palette": "Newar brick and temple gilt", "icon": "pagoda",
                         "ground": "#4A1712", "ground2": "#6B2419", "accent": "#E8B04B", "ink": "#8E3B14", "tint": "#F7E6DA",
                         "grad": ("#2E0C08", "#6B2419", "#9C3A1F"), "foil": ("#FFEBB5", "#E8B04B", "#A86E12")},
    "pokhara-annapurna": {"palette": "Phewa teal and alpenglow", "icon": "fishtail",
                          "ground": "#06333C", "ground2": "#0B4E5A", "accent": "#F7B98C", "ink": "#A04A1E", "tint": "#E0F0F1",
                          "grad": ("#03222A", "#0B4E5A", "#167A85"), "foil": ("#FFE9D9", "#F7B98C", "#D2703F")},
    "everest-khumbu": {"palette": "Glacier night and khata silver", "icon": "everest",
                       "ground": "#0B1D3A", "ground2": "#15315C", "accent": "#CFE3F2", "ink": "#1F4E79", "tint": "#E6EEF6",
                       "grad": ("#060F22", "#15315C", "#2A5A8C"), "foil": ("#FFFFFF", "#CFE3F2", "#86A9C8")},
    "chitwan-terai": {"palette": "Sal forest and elephant-grass gold", "icon": "rhino",
                      "ground": "#12301A", "ground2": "#1C4426", "accent": "#E9C75A", "ink": "#6E5A0E", "tint": "#E7F0DD",
                      "grad": ("#081C0E", "#1C4426", "#2E6A36"), "foil": ("#FFF3BF", "#E9C75A", "#B08A1C")},
    "lumbini": {"palette": "Robe saffron and lotus pink", "icon": "lotus",
                "ground": "#5A2706", "ground2": "#7A390B", "accent": "#F5B3C8", "ink": "#A3375E", "tint": "#FBEBDD",
                "grad": ("#3A1703", "#7A390B", "#B0590F"), "foil": ("#FFE6EE", "#F5B3C8", "#C9668C")},
    "mustang-dolpo": {"palette": "Ochre cliffs and Lo slate", "icon": "chorten",
                      "ground": "#4A200F", "ground2": "#6E3218", "accent": "#A9C1D6", "ink": "#3F5F7E", "tint": "#F4E6D6",
                      "grad": ("#2C1208", "#6E3218", "#A55A2A"), "foil": ("#F1F6FA", "#A9C1D6", "#5E7C99")},
    "langtang-manaslu": {"palette": "Gosaikunda turquoise and Tamang red", "icon": "lake",
                         "ground": "#05363B", "ground2": "#0A5257", "accent": "#F08A78", "ink": "#A83A2C", "tint": "#DFF1EF",
                         "grad": ("#022428", "#0A5257", "#11817C"), "foil": ("#FFE0D9", "#F08A78", "#BF4434")},
    "eastern-nepal": {"palette": "Rhododendron red and Ilam tea", "icon": "rhododendron",
                      "ground": "#4C0E1F", "ground2": "#6E1630", "accent": "#BEDC74", "ink": "#4E6E14", "tint": "#F8E3E8",
                      "grad": ("#2E0612", "#6E1630", "#A42340"), "foil": ("#F3FBD6", "#BEDC74", "#6E9A2A")},
    "far-west": {"palette": "Rara sapphire and Khaptad meadow", "icon": "rara",
                 "ground": "#0C1748", "ground2": "#162870", "accent": "#B8E08A", "ink": "#3F6B1A", "tint": "#E3E8F8",
                 "grad": ("#060C2C", "#162870", "#2A48AE"), "foil": ("#EEFFDC", "#B8E08A", "#6C9F3A")},
}

# Experience kinds, each coded to one of the five lungta (prayer-flag) colours.
KINDS = OrderedDict([
    ("heritage", ("Heritage", "Durbar squares, palaces and old towns", "Walks through squares, courtyards and bahals with guides who grew up in them, timed for the hour the place comes alive.", "yellow")),
    ("spiritual", ("Spiritual", "Stupas, temples, gompas and ghats", "Rituals at their own hours, explained by people who keep them, with the etiquette briefed before you go.", "white")),
    ("trek", ("Trekking", "Trails, passes and teahouses", "Walking days graded honestly by hours, height gained and terrain, with licensed guides and rest days where the body needs them.", "white")),
    ("nature", ("Nature", "Ridges, viewpoints, lakes and forests", "Viewpoints at the right hour, rhododendron forests in season and quiet days outdoors.", "blue")),
    ("wildlife", ("Wildlife", "Rhino, tiger, birds and river dolphins", "Jeep drives, canoe trips and guided walks in the parks of the Terai, matched to the season.", "green")),
    ("water", ("Rivers and lakes", "Boats, rafts and sacred confluences", "Rowing boats at dawn, rafting days on snow-fed rivers and the confluences where Nepalis bathe on festival days.", "green")),
    ("food", ("Food", "Kitchens, feasts and markets", "Cooking with families, feast days and the dishes that explain a valley better than a museum.", "red")),
    ("adventure", ("Adventure", "Paragliding, peaks, bungee and flights", "Active days with operators we know, graded honestly, with weather days built in.", "red")),
    ("craft", ("Craft", "Makers in their workshops", "Potters, woodcarvers, metal casters, weavers and paper makers at work. No commission on what you buy.", "yellow")),
    ("wellness", ("Slow days", "Meditation, yoga and rest", "Retreats, monastery stays and slow mornings planned into the route, not squeezed around it.", "blue")),
])
LUNGTA = {"blue": "#2D5DA8", "white": "#F4F1E8", "red": "#C8322B", "green": "#2E8B57", "yellow": "#E8B931"}

# Altitude belts as we use them on the site (Nepal rises from 59 m to 8,849 m).
BELTS = [
    (0, 300, "Terai", "तराई", "The plains: sal forest, rice, rhino country"),
    (300, 1000, "Chure and Inner Terai", "चुरे", "The first hills and the river valleys behind them"),
    (1000, 2500, "Pahad", "पहाड", "The middle hills: terraces, towns, rhododendron"),
    (2500, 4000, "Lekh", "लेक", "High hills: pasture, pine, the last fields"),
    (4000, 8849, "Himal", "हिमाल", "Ice, moraine and the high passes"),
]
LOWEST_M, HIGHEST_M = 59, 8849

_cache = {"stamp": None, "cat": None}


def _read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _stamp(root):
    return max((p.stat().st_mtime for p in root.rglob("*.json")), default=0)


def catalogue():
    root = Path(settings.CONTENT_DIR)
    if _cache["cat"] is None or settings.DEBUG:
        stamp = _stamp(root)
        if stamp != _cache["stamp"]:
            _cache["cat"] = Catalogue(root)
            _cache["stamp"] = stamp
    return _cache["cat"]


def month_bar(best):
    """[{'m': 'Jan', 'v': 2, 'bs': 'Poush–Magh'}, ...] for the 12-month strip."""
    best = best or [0] * 12
    return [{"m": MONTH_SHORT[i], "full": MONTHS[i], "v": best[i] if i < len(best) else 0,
             "bs": f"{BS_FOR_MONTH[i][0][0]}–{BS_FOR_MONTH[i][1][0]}"} for i in range(12)]


def best_range(best):
    """'Oct – Mar' style label from a 12-int array (rating 2 = best)."""
    if not best:
        return ""
    good = {i for i, v in enumerate(best) if v == 2} or {i for i, v in enumerate(best) if v >= 1}
    if not good:
        return ""
    if len(good) == 12:
        return "All year"
    runs = []
    for i in range(12):
        if i in good and (i - 1) % 12 not in good:
            run, j = [i], (i + 1) % 12
            while j in good:
                run.append(j)
                j = (j + 1) % 12
            runs.append(run)
    return " · ".join(MONTH_SHORT[r[0]] if len(r) == 1 else f"{MONTH_SHORT[r[0]]} – {MONTH_SHORT[r[-1]]}" for r in runs)


def belt(alt):
    for lo, hi, name, ne, note in BELTS:
        if alt is not None and lo <= alt < hi:
            return {"name": name, "ne": ne, "note": note, "lo": lo, "hi": hi}
    return {"name": BELTS[-1][2], "ne": BELTS[-1][3], "note": BELTS[-1][4], "lo": BELTS[-1][0], "hi": BELTS[-1][1]}


def air(alt):
    """What the air is like at this height: oxygen per breath vs sea level, water's boiling point,
    and the temperature difference from Kathmandu (standard atmosphere; real days vary)."""
    if not isinstance(alt, (int, float)):
        return None
    ratio = max(0.0, 1 - 2.25577e-5 * alt) ** 5.25588
    boil_k = 1 / (1 / 373.15 - 8.314 * math.log(ratio) / 40650)
    return {"oxygen": round(ratio * 100), "boil": round(boil_k - 273.15, 1),
            "vs_ktm": round(-(alt - 1400) * 6.5 / 1000, 1), "pct_height": round(100 * alt / HIGHEST_M, 1)}


def contour_svg(seed, rings=9, w=600, h=600):
    """A small topographic contour drawing, unique to each page (seeded by its slug)."""
    rnd = random.Random(seed)
    cx, cy = w * rnd.uniform(0.35, 0.65), h * rnd.uniform(0.35, 0.65)
    phases = [rnd.uniform(0, math.tau) for _ in range(4)]
    amps = [rnd.uniform(0.04, 0.12) for _ in range(4)]
    paths = []
    for k in range(1, rings + 1):
        r0 = k * (min(w, h) / (rings * 1.6))
        pts = []
        for i in range(72):
            a = math.tau * i / 72
            wob = sum(amps[n] * math.sin((n + 2) * a + phases[n] + k * 0.35) for n in range(4))
            r = r0 * (1 + wob)
            pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a) * 0.82:.1f}")
        cls = ' class="ix"' if k % 4 == 0 else ""
        paths.append(f'<path d="M{" L".join(pts)}Z"{cls}/>')
    return (f'<svg class="contours" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'{"".join(paths)}</svg>')


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


class Catalogue:
    def __init__(self, root):
        self.root = root
        self.themes = OrderedDict((t["slug"], t) for t in _read(root / "themes.json"))
        img_file = root / "images.json"
        self.images = _read(img_file) if img_file.exists() else {}
        self.regions = OrderedDict()
        self.places = OrderedDict()
        self.experiences = OrderedDict()
        self.journeys = OrderedDict()
        self.stays = OrderedDict()
        self.guides = OrderedDict()
        self.festivals = OrderedDict()
        self.routes = OrderedDict()
        for slug in REGION_ORDER:
            base = root / slug
            if (base / "region.json").exists():
                self._load_region(slug, base)
        self.posts = OrderedDict()
        for p in (root / "stories").glob("*.json") if (root / "stories").exists() else []:
            d = _read(p)
            d["url"] = reverse("post", args=[d["slug"]])
            self.posts[d["slug"]] = d
        self.posts = OrderedDict(sorted(self.posts.items(), key=lambda kv: kv[1].get("date", ""), reverse=True))
        self._link()
        self._link_posts()
        self._collect()

    # ---------- loading ----------
    def _load_region(self, slug, base):
        r = _read(base / "region.json")
        r["slug"] = slug
        r.update(LANDS[slug])
        r["url"] = reverse("region", args=[slug])
        r["places"], r["journeys"], r["stays"], r["guides"], r["festivals"], r["routes"] = [], [], [], [], [], []
        self.regions[slug] = r
        for p in sorted((base / "places").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("place", args=[slug, d["slug"]])
            self.places[d["slug"]] = d
            r["places"].append(d)
            for e in d.get("experiences", []):
                e["place"] = d["slug"]
                e["region"] = slug
                e["url"] = reverse("experience", args=[slug, d["slug"], e["slug"]])
                self.experiences[e["slug"]] = e
        for p in sorted((base / "journeys").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("journey", args=[d["slug"]])
            self.journeys[d["slug"]] = d
            r["journeys"].append(d)
        for name, store, key, view in (("stays.json", self.stays, "stays", "stay"),
                                       ("festivals.json", self.festivals, "festivals", "festival"),
                                       ("routes.json", self.routes, "routes", "route")):
            f = base / name
            for d in (_read(f) if f.exists() else []):
                d["region"] = slug
                d["url"] = reverse(view, args=[d["slug"]])
                store[d["slug"]] = d
                r[key].append(d)
        for p in sorted((base / "guides").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("guide", args=[d["slug"]])
            self.guides[d["slug"]] = d
            r["guides"].append(d)

    @staticmethod
    def _lead_unique(imgs, used):
        """Put the first photo not yet used as a lead elsewhere in front, so neighbouring cards differ.
        Falls back to the original order when every photo is already taken."""
        for i, im in enumerate(imgs):
            if im["file"] not in used:
                used.add(im["file"])
                return imgs[i:] + imgs[:i]
        return imgs

    def _imgs(self, *keys):
        for k in keys:
            if self.images.get(k):
                return self.images[k]
        return []

    def _link(self):
        for slug in [s for s, rt in self.routes.items() if rt.get("from") not in self.places or rt.get("to") not in self.places]:
            dead = self.routes.pop(slug)
            self.regions[dead["region"]]["routes"].remove(dead)
        for p in self.places.values():
            r = self.regions[p["region"]]
            p["region_obj"] = r
            p["images"] = self._imgs(f"place:{p['slug']}")
            p["best_label"] = best_range(p.get("best_months"))
            p["bar"] = month_bar(p.get("best_months"))
            p["belt"] = belt(p.get("altitude_m"))
            p["air"] = air(p.get("altitude_m"))
            p["nearby_objs"] = [self.places[s] for s in p.get("nearby", []) if s in self.places]
            p["stay_objs"] = [self.stays[s] for s in p.get("stays", []) if s in self.stays]
            p["journey_objs"] = [j for j in self.journeys.values()
                                 if any(s["place"] == p["slug"] for s in j.get("stops", []))]
            p["festival_objs"] = [f for f in self.festivals.values() if f.get("place") == p["slug"]]
            p["route_objs"] = [rt for rt in self.routes.values() if p["slug"] in (rt.get("from"), rt.get("to"))]
        for r in self.regions.values():
            r["top_places"] = sorted(r["places"], key=lambda p: (-len(p["journey_objs"]), p["name"]))
            r["images"] = self._imgs(f"region:{r['slug']}") or [
                i for p in r["top_places"][:6] for i in p["images"][:1]]
            r["best_label"] = best_range(r.get("best_months"))
            r["bar"] = month_bar(r.get("best_months"))
            alts = [p["altitude_m"] for p in r["places"] if isinstance(p.get("altitude_m"), int)]
            r["alt_lo"] = r.get("altitude_min_m") or (min(alts) if alts else 0)
            r["alt_hi"] = r.get("altitude_max_m") or (max(alts) if alts else 0)
            r["by_height"] = sorted(r["places"], key=lambda p: p.get("altitude_m") or 0)
        for e in self.experiences.values():
            place = self.places[e["place"]]
            e["place_obj"] = place
            e["region_obj"] = place["region_obj"]
            e["images"] = self._imgs(f"exp:{e['slug']}") or place["images"][1:] or place["images"]
            e["themes"] = place.get("themes", [])
            e["flag"] = KINDS.get(e.get("kind"), ("", "", "", "white"))[3]
        for s in self.stays.values():
            place = self.places.get(s.get("place"))
            s["place_obj"] = place
            s["region_obj"] = self.regions[s["region"]]
            s["images"] = self._imgs(f"stay:{s['slug']}") or (place["images"] if place else [])
            s["journey_objs"] = [j for j in self.journeys.values() if s["slug"] in j.get("stays", [])]
        for j in self.journeys.values():
            j["region_obj"] = self.regions[j["region"]]
            stops = [dict(st, obj=self.places[st["place"]]) for st in j.get("stops", []) if st["place"] in self.places]
            j["stop_objs"] = stops
            j["images"] = self._imgs(f"journey:{j['slug']}") or [
                i for st in stops for i in st["obj"]["images"][:1]]
            j["stay_objs"] = [self.stays[s] for s in j.get("stays", []) if s in self.stays]
            j["best_label"] = best_range(j.get("best_months"))
            j["bar"] = month_bar(j.get("best_months"))
            j["days_count"] = j.get("nights", 0) + 1
            for d in j.get("days", []):
                d["place_obj"] = self.places.get(d.get("place"))
            j["profile"] = self._profile(j)
        for g in self.guides.values():
            g["region_obj"] = self.regions[g["region"]]
            rel = [self.places[s] for s in g.get("related_places", []) if s in self.places]
            g["related_objs"] = rel
            g["images"] = self._imgs(f"guide:{g['slug']}") or [i for p in rel for i in p["images"][:1]] or g["region_obj"]["images"]
            words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in g.get("sections", []))
            g["read_min"] = max(3, round(words / 220))
            for s in g.get("sections", []):
                s["anchor"] = slugify(s.get("heading"))
        for f in self.festivals.values():
            place = self.places.get(f.get("place"))
            f["place_obj"] = place
            f["region_obj"] = self.regions[f["region"]]
            f["images"] = self._imgs(f"fest:{f['slug']}") or (place["images"] if place else [])
        for rt in self.routes.values():
            rt["from_obj"] = self.places.get(rt.get("from"))
            rt["to_obj"] = self.places.get(rt.get("to"))
            rt["region_obj"] = self.regions[rt["region"]]
            rt["images"] = (rt["to_obj"] or {}).get("images", []) + (rt["from_obj"] or {}).get("images", [])[:1]
        for t in self.themes.values():
            t["url"] = reverse("theme", args=[t["slug"]])
        self._dedupe_leads()

    def _dedupe_leads(self):
        """No two places, trips, experiences, stays, festivals, guides or routes lead with the same photo."""
        used = set()
        for p in self.places.values():
            p["images"] = self._lead_unique(p["images"], used)
        for r in self.regions.values():
            if not self.images.get(f"region:{r['slug']}"):
                r["images"] = [i for p in r["top_places"][:6] for i in p["images"][:1]]
        for store in (self.stays, self.festivals, self.guides, self.routes):
            used = set()
            for o in store.values():
                o["images"] = self._lead_unique(o.get("images") or [], used)
        used = set()
        for e in self.experiences.values():
            own = self.images.get(f"exp:{e['slug']}")
            pool = list(own) if own else list(e["place_obj"]["images"])
            if not own:  # inherited from the place: borrow every photo the place has, not just the spare ones
                pool = pool[1:] + pool[:1]
            e["images"] = self._lead_unique(pool, used)
        used = set()
        for j in self.journeys.values():
            own = self.images.get(f"journey:{j['slug']}")
            pool = list(own) if own else [i for st in j["stop_objs"] for i in st["obj"]["images"]]
            j["images"] = self._lead_unique(pool, used)

    @staticmethod
    def _profile(j):
        """Elevation profile of a journey, one point per night, as SVG path data (viewBox 0 0 600 160)."""
        days = j.get("days") or []
        alts = [d.get("alt_m") for d in days if isinstance(d.get("alt_m"), int)]
        if len(alts) < 2:
            return None
        hi = max(alts)
        top = max(1500, math.ceil(hi / 1000) * 1000)
        n = len(alts)
        pts = [(round(20 + 560 * i / (n - 1), 1), round(140 - 120 * a / top, 1)) for i, a in enumerate(alts)]
        line = "M" + " L".join(f"{x},{y}" for x, y in pts)
        area = line + f" L{pts[-1][0]},140 L{pts[0][0]},140 Z"
        peak_i = alts.index(hi)
        grid = [{"y": round(140 - 120 * v / top, 1), "label": f"{v:,} m"} for v in range(0, top + 1, max(1000, top // 4 // 1000 * 1000))]
        return {"line": line, "area": area, "pts": [{"x": x, "y": y, "alt": a, "day": i + 1} for i, ((x, y), a) in enumerate(zip(pts, alts))],
                "peak": {"x": pts[peak_i][0], "y": pts[peak_i][1], "alt": hi, "day": peak_i + 1},
                "grid": grid, "max": hi, "gain": sum(max(0, b - a) for a, b in zip(alts, alts[1:]))}

    def _link_posts(self):
        from datetime import date
        for d in self.posts.values():
            d["region_objs"] = [self.regions[r] for r in d.get("regions", []) if r in self.regions]
            d["journey_objs"] = [self.journeys[j] for j in d.get("related_journeys", []) if j in self.journeys]
            d["place_objs"] = [self.places[x] for x in d.get("related_places", []) if x in self.places]
            d["images"] = (self._imgs(f"blog:{d['slug']}") or [i for x in d["place_objs"] for i in x["images"][:1]])
            words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in d.get("sections", []))
            d["read_min"] = max(3, round(words / 220))
            d["cat_slug"] = slugify(d.get("category"))
            try:
                d["date_obj"] = date.fromisoformat(d.get("date", ""))
            except ValueError:
                d["date_obj"] = None
            d["land"] = d["region_objs"][0]["slug"] if d["region_objs"] else None
            stores = {"journey": self.journeys, "place": self.places, "stay": self.stays, "guide": self.guides, "festival": self.festivals}
            for sec in d.get("sections", []):
                sec["anchor"] = slugify(sec.get("heading"))
                objs = []
                for ln in sec.get("links", []):
                    o = stores.get(ln.get("type"), {}).get(ln.get("slug"))
                    if o:
                        objs.append({"type": ln["type"], "title": o.get("title") or o.get("name"), "url": o["url"],
                                     "img": (o.get("images") or [None])[0]})
                sec["link_objs"] = objs
        self.post_categories = OrderedDict()
        for d in self.posts.values():
            self.post_categories.setdefault(d["cat_slug"], {"slug": d["cat_slug"], "name": d.get("category"), "posts": []})["posts"].append(d)

    def _collect(self):
        """Site-wide story collections: words, untold facts, legends, peoples."""
        self.words, self.untold, self.legends = [], [], []
        seen = set()
        for owner in list(self.regions.values()) + list(self.places.values()):
            is_region = "places" in owner
            r = owner if is_region else owner["region_obj"]
            for w in owner.get("local_words", []):
                key = (w.get("word") or "").lower()
                if key and key not in seen:
                    seen.add(key)
                    self.words.append(dict(w, where=owner["name"], url=owner["url"], region=r["slug"]))
            for u in owner.get("untold", []):
                self.untold.append(dict(u, where=owner["name"], url=owner["url"], region=r["slug"]))
            if owner.get("legend"):
                self.legends.append({"text": owner["legend"], "where": owner["name"], "url": owner["url"],
                                     "region": r["slug"], "name_ne": owner.get("name_ne", ""),
                                     "images": owner.get("images", [])})
        self.words.sort(key=lambda w: w.get("word", "").lower())

    # ---------- queries ----------
    def theme_items(self, theme, region=None):
        def ok(x):
            return region is None or x.get("region") == region
        places = [p for p in self.places.values() if theme in p.get("themes", []) and ok(p)]
        journeys = [j for j in self.journeys.values() if theme in j.get("themes", []) and ok(j)]
        place_slugs = {p["slug"] for p in places}
        stays = [s for s in self.stays.values() if s.get("place") in place_slugs and ok(s)]
        experiences = [e for e in self.experiences.values() if e["place"] in place_slugs and ok(e)]
        return {"places": places, "journeys": journeys, "stays": stays, "experiences": experiences}

    def region_theme_pairs(self):
        out = []
        for r in self.regions:
            for t in self.themes:
                items = self.theme_items(t, r)
                if len(items["places"]) >= 2 and (items["journeys"] or len(items["places"]) >= 3):
                    out.append((r, t))
        return out

    def region_kind_pairs(self):
        out = []
        for r in self.regions:
            for k in KINDS:
                if sum(1 for e in self.experiences.values() if e["region"] == r and e.get("kind") == k) >= 3:
                    out.append((r, k))
        return out

    def counts(self):
        return {
            "regions": len(self.regions), "places": len(self.places), "experiences": len(self.experiences),
            "journeys": len(self.journeys), "stays": len(self.stays), "guides": len(self.guides),
            "festivals": len(self.festivals), "routes": len(self.routes), "themes": len(self.themes),
            "posts": len(self.posts),
        }

    def all_images(self):
        seen, out = set(), []
        for key, recs in self.images.items():
            for rec in recs:
                if rec["file"] not in seen:
                    seen.add(rec["file"])
                    out.append(dict(rec, used_for=key))
        return out


# ---------- the home-page cross-section: Nepal from the Terai to the Tibetan plateau ----------
_XS_POINTS = [(0, 70), (.08, 90), (.16, 140), (.19, 350), (.215, 950), (.235, 600), (.26, 280), (.29, 300),
              (.31, 1300), (.335, 2450), (.36, 1700), (.40, 1350), (.44, 1900), (.48, 1300), (.52, 2100),
              (.56, 1500), (.60, 2300), (.64, 2900), (.68, 3600), (.72, 4300), (.76, 5600), (.79, 6900),
              (.81, 5900), (.84, 7600), (.86, 6600), (.885, 8849), (.905, 7300), (.93, 8100), (.95, 6400),
              (.975, 5400), (1.0, 4900)]


def _xs_alt(t, shift=0.0, scale=1.0, seed=0):
    t = min(1.0, max(0.0, t + shift))
    for (x0, a0), (x1, a1) in zip(_XS_POINTS, _XS_POINTS[1:]):
        if x0 <= t <= x1:
            a = a0 + (a1 - a0) * (t - x0) / (x1 - x0 or 1)
            break
    else:
        a = _XS_POINTS[-1][1]
    if a < 8849:
        a += math.sin(t * 310 + seed) * min(a * .05, 220) + math.sin(t * 97 + seed * 2) * min(a * .03, 140)
    return max(40.0, a * scale)


def cross_section(w=1600, h=520, n=240):
    """Layered ridgelines (back to front) plus sampled altitudes for the interactive readout."""
    base, top = h - 30, 60

    def y(a):
        return base - a * (base - top) / HIGHEST_M

    layers = []
    for shift, scale, seed, cls in ((.025, .82, 1.3, "l3"), (-.018, .92, 2.1, "l2"), (0, 1, 0, "l1")):
        pts = [(w * i / n, y(_xs_alt(i / n, shift, scale, seed))) for i in range(n + 1)]
        line = "M" + " L".join(f"{x:.1f},{yy:.1f}" for x, yy in pts)
        layers.append({"cls": cls, "line": line, "area": line + f" L{w},{h} L0,{h} Z"})
    samples = [round(_xs_alt(i / n)) for i in range(n + 1)]
    peak_i = max(range(n + 1), key=lambda i: samples[i])
    samples[peak_i] = HIGHEST_M
    belts = [{"name": b[2], "ne": b[3], "x": w * x} for b, x in zip(BELTS, (.075, .235, .47, .67, .86))]
    grid = [{"y": round(y(a), 1), "label": f"{a:,} m"} for a in (0, 2000, 4000, 6000, 8000)]
    return {"w": w, "h": h, "layers": layers, "samples": samples, "belts": belts, "grid": grid,
            "peak": {"x": round(w * peak_i / n, 1), "y": round(y(HIGHEST_M), 1)}, "base": base, "top": top}
