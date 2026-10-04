"""Validate one region's content against content/SCHEMA.md.

Usage: python tools/check_region.py <region-slug> [--part core|journeys] [--wiki]
  --part core      region.json, places, stays, festivals, routes
  --part journeys  journeys and guides
  --wiki           also confirm every `wiki` title exists on English Wikipedia
"""
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "content"
THEMES = set("treks-and-trails high-altitude heritage-and-temples wildlife-and-jungle spiritual-and-pilgrimage "
             "food-and-festivals villages-and-homestays lakes-and-rivers family-trips honeymoons photography "
             "adventure-sports crafts-and-makers slow-and-wellness".split())
KINDS = set("heritage spiritual nature wildlife food adventure trek water craft wellness".split())
BANNED = ["nestled", "breathtaking", "hidden gem", "paradise", "tapestry", "embark", "delve", "unleash",
          "vibrant", "bustling", "mesmeriz", "stunning", "magical", "heaven on earth", "feast for the eyes",
          "something for everyone", "whether you're", "look no further", "ultimate guide", "in this blog",
          "in conclusion", "unforgettable", "world-class", "seamless", "elevate", "immerse", "timeless",
          "boasts", "roof of the world", "land of contrasts", "off the beaten path", "shangri-la", "!"]
errors, warns = [], []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception as e:  # noqa: BLE001
        err(p, f"invalid JSON ({e})")
        return None


def months(where, v):
    if not (isinstance(v, list) and len(v) == 12 and all(x in (0, 1, 2) for x in v)):
        err(where, "best_months must be 12 ints of 0/1/2")


def faqs(where, v, n):
    if not isinstance(v, list) or len(v) != n:
        err(where, f"needs exactly {n} faqs (has {len(v) if isinstance(v, list) else 0})")
        return
    for f in v:
        if not f.get("q") or not f.get("a"):
            err(where, "faq missing q/a")


def heading(where, t):
    if t and t.rstrip().endswith("."):
        err(where, f"heading ends with full stop: {t!r}")


def scan_banned(where, obj):
    text = json.dumps(obj, ensure_ascii=False).lower()
    for b in BANNED:
        if b in text:
            warns.append(f"{where}: banned word/phrase '{b}'")


def story(where, d, n_untold=3, n_words=3):
    s = d.get("story") or {}
    if not s.get("title") or len(s.get("paras", [])) < 3:
        err(where, "story needs title and >= 3 paras")
    heading(where, s.get("title"))
    if not d.get("people"):
        err(where, "missing people")
    if len(d.get("untold", [])) != n_untold:
        err(where, f"needs exactly {n_untold} untold facts")
    for u in d.get("untold", []):
        if not u.get("fact") or not u.get("source"):
            err(where, "untold item needs fact and source")
    if len(d.get("local_words", [])) != n_words:
        err(where, f"needs exactly {n_words} local_words")
    if not (d.get("taste") or {}).get("name"):
        err(where, "missing taste")


def main():
    r = sys.argv[1]
    part = sys.argv[sys.argv.index("--part") + 1] if "--part" in sys.argv else "all"
    plan = json.loads((ROOT / "_plan.json").read_text(encoding="utf-8"))
    mine = next((x for x in plan["regions"] if x["slug"] == r), None)
    if not mine:
        sys.exit(f"unknown region {r}")
    all_places = {p for x in plan["regions"] for p in x["places"]}
    all_stays = {s for x in plan["regions"] for s in x["stays"]}
    base = ROOT / r
    wiki_titles = []

    if part in ("all", "core"):
        reg = load(base / "region.json")
        places = {}
        for p in sorted((base / "places").glob("*.json")):
            d = load(p)
            if d:
                places[d["slug"]] = d
                if p.stem != d["slug"]:
                    err(p.name, "file name must equal slug")
        stays = {s["slug"]: s for s in (load(base / "stays.json") or [])}
        fests = {f["slug"]: f for f in (load(base / "festivals.json") or [])}
        missing = set(mine["places"]) - set(places)
        if missing:
            err("places", f"missing place files: {sorted(missing)}")
        for extra in set(places) - set(mine["places"]):
            err("places", f"place '{extra}' is not in _plan.json")
        if reg is None:
            err("region", "region.json missing")
        else:
            months("region", reg.get("best_months"))
            faqs("region", reg.get("faqs"), 9)
            story("region", reg, 5, 5)
            if len(reg.get("highlights", [])) != 6:
                err("region", "needs 6 highlights")
            if len(reg.get("months", [])) != 12:
                err("region", "needs 12 months")
            for m in reg.get("months", []):
                for g in m.get("go", []):
                    if g not in places:
                        err(f"region month {m.get('month')}", f"unknown place '{g}'")
                for e in m.get("events", []):
                    if e not in fests:
                        err(f"region month {m.get('month')}", f"unknown festival '{e}'")
            wiki_titles.append(reg.get("wiki"))
            scan_banned("region", reg)

        exp_slugs = set()
        for slug, d in places.items():
            w = f"place {slug}"
            months(w, d.get("best_months"))
            faqs(w, d.get("faqs"), 9)
            heading(w, d.get("tagline"))
            story(w, d)
            if not isinstance(d.get("altitude_m"), int):
                err(w, "altitude_m must be an integer")
            for t in d.get("themes", []):
                if t not in THEMES:
                    err(w, f"unknown theme '{t}'")
            for n in d.get("nearby", []):
                if n not in places:
                    err(w, f"unknown nearby '{n}'")
            for s in d.get("stays", []):
                if s not in stays:
                    err(w, f"unknown stay '{s}'")
            ex = d.get("experiences", [])
            if len(ex) != 4:
                err(w, f"needs 4 experiences (has {len(ex)})")
            for e in ex:
                heading(f"{w} exp", e.get("title"))
                faqs(f"{w} exp {e.get('slug')}", e.get("faqs"), 3)
                if e.get("kind") not in KINDS:
                    err(w, f"experience {e.get('slug')} unknown kind '{e.get('kind')}'")
                if e["slug"] in exp_slugs:
                    err(w, f"duplicate experience slug {e['slug']}")
                exp_slugs.add(e["slug"])
                if e.get("wiki"):
                    wiki_titles.append(e["wiki"])
            wiki_titles.append(d.get("wiki"))
            scan_banned(w, d)

        for slug, s in stays.items():
            w = f"stay {slug}"
            faqs(w, s.get("faqs"), 3)
            if slug not in mine["stays"]:
                err(w, "not in _plan.json")
            if s.get("place") not in places:
                err(w, f"unknown place '{s.get('place')}'")
            if s.get("wiki"):
                wiki_titles.append(s["wiki"])
            scan_banned(w, s)

        for slug, f in fests.items():
            w = f"festival {slug}"
            faqs(w, f.get("faqs"), 4)
            if f.get("place") not in places:
                err(w, f"unknown place '{f.get('place')}'")
            if f.get("wiki"):
                wiki_titles.append(f["wiki"])
            scan_banned(w, f)

        routes = load(base / "routes.json") or []
        for rt in routes:
            w = f"route {rt.get('slug')}"
            faqs(w, rt.get("faqs"), 4)
            for k in ("from", "to"):
                if rt.get(k) not in all_places:
                    err(w, f"unknown {k} '{rt.get(k)}'")
            scan_banned(w, rt)
        print(f"core: places={len(places)} experiences={len(exp_slugs)} stays={len(stays)} "
              f"festivals={len(fests)} routes={len(routes)}")

    if part in ("all", "journeys"):
        nj = ng = 0
        for p in sorted((base / "journeys").glob("*.json")):
            d = load(p)
            if not d:
                continue
            nj += 1
            w = f"journey {d.get('slug')}"
            months(w, d.get("best_months"))
            faqs(w, d.get("faqs"), 9)
            heading(w, d.get("title"))
            if not d.get("story"):
                err(w, "missing story")
            if not isinstance(d.get("price_from_usd"), int):
                err(w, "price_from_usd must be an integer")
            total = sum(s.get("nights", 0) for s in d.get("stops", []))
            if total != d.get("nights"):
                err(w, f"stop nights {total} != nights {d.get('nights')}")
            if len(d.get("days", [])) != d.get("nights", 0) + 1:
                err(w, "days must equal nights + 1")
            for day in d.get("days", []):
                if not isinstance(day.get("alt_m"), int):
                    err(w, f"day {day.get('day')} alt_m must be an integer")
                if day.get("place") and day["place"] not in all_places:
                    err(w, f"day {day.get('day')} unknown place '{day['place']}'")
            for s in d.get("stops", []):
                if s["place"] not in all_places:
                    err(w, f"unknown stop '{s['place']}'")
            for s in d.get("stays", []):
                if s not in all_stays:
                    err(w, f"unknown stay '{s}'")
            for t in d.get("themes", []):
                if t not in THEMES:
                    err(w, f"unknown theme '{t}'")
            scan_banned(w, d)
        for p in sorted((base / "guides").glob("*.json")):
            d = load(p)
            if not d:
                continue
            ng += 1
            w = f"guide {d.get('slug')}"
            faqs(w, d.get("faqs"), 9)
            heading(w, d.get("title"))
            words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in d.get("sections", []))
            if words < 1000:
                warns.append(f"{w}: only {words} words")
            for s in d.get("sections", []):
                heading(w, s.get("heading"))
            for rp in d.get("related_places", []):
                if rp not in all_places:
                    err(w, f"unknown related place '{rp}'")
            scan_banned(w, d)
        print(f"journeys={nj} guides={ng}")

    if "--wiki" in sys.argv:
        titles = sorted({t for t in wiki_titles if t})
        for i in range(0, len(titles), 40):
            q = urllib.parse.urlencode({"action": "query", "titles": "|".join(titles[i:i + 40]),
                                        "redirects": 1, "format": "json", "formatversion": 2})
            req = urllib.request.Request("https://en.wikipedia.org/w/api.php?" + q,
                                         headers={"User-Agent": "BookNepalTripBuild/1.0"})
            data = json.load(urllib.request.urlopen(req, timeout=30))
            for pg in data["query"]["pages"]:
                if pg.get("missing"):
                    err("wiki", f"no Wikipedia article titled {pg['title']!r} (use '' or fix)")

    for w in warns:
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
