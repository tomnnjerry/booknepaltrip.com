"""Fill photo gaps: retry every place, stay and festival that has no credited photo.

Usage: python tools/fill_missing_images.py

For each gap it tries, in order: the Wikipedia article, the hand-written image_query, then looser Commons
searches ("<name> Nepal", "<name> <region>", "<name>"), first at the normal size floor and then with a lower one.
Run `python tools/smoke.py` afterwards, then commit content/images.json.
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import commons  # noqa: E402
from fetch_images import BAD_TITLE, OUT, clean, landscape_first, read  # noqa: E402

CONTENT = Path(__file__).resolve().parent.parent / "content"


def gaps(images):
    jobs = []
    for region in sorted(p for p in CONTENT.iterdir() if (p / "region.json").exists()):
        rname = read(region / "region.json").get("name", "Nepal")
        for f in sorted((region / "places").glob("*.json")):
            d = read(f)
            if not images.get(f"place:{d['slug']}"):
                jobs.append((f"place:{d['slug']}", d))
        for name, key in (("stays.json", "stay"), ("festivals.json", "fest")):
            if (region / name).exists():
                for d in read(region / name):
                    if not images.get(f"{key}:{d['slug']}"):
                        jobs.append((f"{key}:{d['slug']}", d))
        for j in jobs:
            j[1].setdefault("_region", rname)
    return jobs


def attempt(d, n=5):
    name = d.get("name") or d.get("title")
    rname = d.get("_region", "")
    queries = [q for q in (d.get("image_query"), f"{name} Nepal", f"{name} {rname}", name) if q]
    for floor in ((1000, 600), (640, 400)):
        commons.MIN_W, commons.MIN_H = floor
        recs = []
        if d.get("wiki"):
            recs += commons.article_images(d["wiki"], n + 2)
        for q in queries:
            if len(clean(recs)) >= n:
                break
            recs += commons.search_images(q, n)
        recs = [r for r in clean(recs) if not BAD_TITLE.search(r["file"])]
        if recs:
            return landscape_first(recs)[:n]
    return []


def main():
    images = read(OUT)
    jobs = gaps(images)
    print(f"{len(jobs)} gaps")

    def run(job):
        key, d = job
        try:
            return key, attempt(d)
        except Exception as e:  # noqa: BLE001
            print("  fail", key, e)
            return key, []

    # one worker at a time: Commons rate-limits parallel bursts, which is how these gaps appeared
    with ThreadPoolExecutor(max_workers=1) as pool:
        for key, recs in pool.map(run, jobs):
            if recs:
                images[key] = recs
            print(("  filled " if recs else "  still empty ") + key)
    OUT.write_text(json.dumps(images, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
