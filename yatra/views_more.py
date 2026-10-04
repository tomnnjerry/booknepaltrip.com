"""Journal, policies, contact, how-we-work, newsletter and search index."""
import json

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .content import catalogue
from .forms import EnquiryForm, SubscribeForm
from .models import Subscriber
from .policies import POLICIES, UPDATED
from .views import COMPANY_FAQS, _get, crumbs, faq_ld, img_url, ld, org_ld


def journal(request, cat=None):
    c = catalogue()
    posts = list(c.posts.values())
    category = None
    if cat:
        category = c.post_categories.get(cat)
        if not category:
            raise Http404
        posts = category["posts"]
    trail = [("Stories", reverse("journal"))] + ([(category["name"], request.path)] if category else [])
    items, bc = crumbs(*trail)
    return render(request, "yatra/journal.html", {"posts": posts, "category": category,
                                                  "cats": list(c.post_categories.values()), "crumbs": items, "ld": ld(bc)})


def post(request, slug):
    c = catalogue()
    d = _get(c.posts, slug)
    items, bc = crumbs(("Stories", reverse("journal")), (d["title"], d["url"]))
    article = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": d["title"],
               "description": d.get("summary"), "datePublished": d.get("date"), "image": img_url(d),
               "author": {"@type": "Organization", "name": settings.SITE["byline"]},
               "publisher": {"@type": "Organization", "name": settings.SITE["name"]}}
    more = [x for x in c.posts.values() if x is not d and (
        x["cat_slug"] == d["cat_slug"] or set(x.get("regions", [])) & set(d.get("regions", [])))][:3]
    return render(request, "yatra/post.html", {"d": d, "more": more, "crumbs": items,
                                               "ld": ld(bc, article, faq_ld(d.get("faqs", [])))})


def policies(request):
    items, bc = crumbs(("Policies", reverse("policies")))
    return render(request, "yatra/policies.html", {"policies": [dict(v, slug=k) for k, v in POLICIES.items()],
                                                   "crumbs": items, "ld": ld(bc)})


def policy(request, slug):
    pol = POLICIES.get(slug)
    if not pol:
        raise Http404
    items, bc = crumbs(("Policies", reverse("policies")), (pol["title"], request.path))
    sections = [{"heading": h, "blocks": [b if isinstance(b, dict) else {"p": b} for b in body]} for h, body in pol["sections"]]
    others = [(k, v["nav"]) for k, v in POLICIES.items() if k != slug]
    return render(request, "yatra/policy.html", {"pol": pol, "slug": slug, "sections": sections, "others": others,
                                                 "updated": UPDATED, "crumbs": items, "ld": ld(bc)})


def contact(request):
    items, bc = crumbs(("Contact", reverse("contact")))
    form = EnquiryForm(initial={"source_page": request.path, "kind": "quick"})
    return render(request, "yatra/contact.html", {"form": form, "crumbs": items, "ld": ld(bc, org_ld())})


def how_we_work(request):
    items, bc = crumbs(("How we work", reverse("how_we_work")))
    return render(request, "yatra/how_we_work.html", {"crumbs": items, "counts": catalogue().counts(),
                                                      "faqs": COMPANY_FAQS[:6], "ld": ld(bc, faq_ld(COMPANY_FAQS[:6]))})


def subscribe(request):
    if request.method != "POST":
        return redirect("home")
    form = SubscribeForm(request.POST)
    ok = form.is_valid() and not form.cleaned_data.get("website")
    if ok:
        Subscriber.objects.get_or_create(email=form.cleaned_data["email"].lower(),
                                         defaults={"source_page": form.cleaned_data.get("source_page", "")[:300]})
    return render(request, "yatra/subscribed.html", {"ok": ok, "crumbs": crumbs(("Stories", reverse("journal")))[0]})


def search_index(request):
    """Compact JSON index for the on-site search overlay: [title, url, kind, context]."""
    c = catalogue()
    rows = [[r["name"], r["url"], "Region", r.get("name_ne", "")] for r in c.regions.values()]
    rows += [[p["name"], p["url"], "Place", p["region_obj"]["name"]] for p in c.places.values()]
    rows += [[j["title"], j["url"], f"Trip · {j['nights']} nights", j["region_obj"]["name"]] for j in c.journeys.values()]
    rows += [[e["title"], e["url"], "Experience", e["place_obj"]["name"]] for e in c.experiences.values()]
    rows += [[s["name"], s["url"], "Stay", s["region_obj"]["name"]] for s in c.stays.values()]
    rows += [[g["title"], g["url"], "Guide", g["region_obj"]["name"]] for g in c.guides.values()]
    rows += [[d["title"], d["url"], "Story", d.get("category", "")] for d in c.posts.values()]
    rows += [[f["name"], f["url"], "Festival", f["region_obj"]["name"]] for f in c.festivals.values()]
    rows += [[t["name"], t["url"], "Style", ""] for t in c.themes.values()]
    resp = HttpResponse(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), content_type="application/json")
    resp["Cache-Control"] = "public, max-age=3600"
    return resp


# ---------------- story hubs: words, untold facts, legends, Nepal by height ----------------
def words(request):
    c = catalogue()
    items, bc = crumbs(("Words you will hear", reverse("words")))
    langs = sorted({w.get("lang", "") for w in c.words if w.get("lang")})
    term_ld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "Words you will hear in Nepal",
               "hasDefinedTerm": [{"@type": "DefinedTerm", "name": w["word"], "description": w.get("meaning", "")} for w in c.words[:300]]}
    return render(request, "yatra/words.html", {"words": c.words, "langs": langs, "regions": list(c.regions.values()),
                                                "crumbs": items, "ld": ld(bc, term_ld)})


def untold(request):
    c = catalogue()
    items, bc = crumbs(("Untold Nepal", reverse("untold")))
    groups = [{"r": r, "facts": [u for u in c.untold if u["region"] == r["slug"]]} for r in c.regions.values()]
    return render(request, "yatra/untold.html", {"groups": groups, "crumbs": items, "ld": ld(bc)})


def legends(request):
    c = catalogue()
    items, bc = crumbs(("Legends", reverse("legends")))
    groups = [{"r": r, "legends": [x for x in c.legends if x["region"] == r["slug"]]} for r in c.regions.values()]
    return render(request, "yatra/legends.html", {"groups": groups, "crumbs": items, "ld": ld(bc)})


def altitude(request):
    from .content import BELTS, HIGHEST_M, LOWEST_M
    c = catalogue()
    items, bc = crumbs(("Nepal by height", reverse("altitude")))
    places = sorted([p for p in c.places.values() if isinstance(p.get("altitude_m"), int)], key=lambda p: -p["altitude_m"])
    belts = [{"name": n, "ne": ne, "note": note, "lo": lo, "hi": hi,
              "places": [p for p in places if lo <= p["altitude_m"] < hi or (hi == HIGHEST_M and p["altitude_m"] >= lo)]}
             for lo, hi, n, ne, note in reversed(BELTS)]
    return render(request, "yatra/altitude.html", {"belts": belts, "lowest": LOWEST_M, "highest": HIGHEST_M,
                                                   "crumbs": items, "ld": ld(bc)})


def tool_altitude(request):
    from .content import air
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Altitude and air", reverse("tool_altitude")))
    c = catalogue()
    marks = [{"n": p["name"], "a": p["altitude_m"], "u": p["url"]} for p in c.places.values() if isinstance(p.get("altitude_m"), int)]
    marks.sort(key=lambda m: m["a"])
    return render(request, "yatra/tool_altitude.html", {"crumbs": items, "ld": ld(bc), "marks": json.dumps(marks).replace("</", "<\/"),
                                                        "sample": [dict(n=n, a=a, **air(a)) for n, a in
                                                                   (("Kathmandu", 1400), ("Namche Bazaar", 3440), ("Everest Base Camp", 5364), ("Thorong La", 5416))]})


def icon_sheet(request):
    from .icons import ICONS
    items, bc = crumbs(("Icons", request.path))
    return render(request, "yatra/icons.html", {"names": list(ICONS), "crumbs": items, "ld": ld(bc)})
