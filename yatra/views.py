import json
from datetime import date

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .content import BELTS, BS_FOR_MONTH, HIGHEST_M, KINDS, LOWEST_M, MONTH_SHORT, MONTHS, air, belt, catalogue, contour_svg, month_bar
from .forms import EnquiryForm, SubscribeForm
from .models import Subscriber
from .policies import POLICIES, UPDATED

COMPANY_FAQS = [
    {"q": "What does Book Nepal Trip do?",
     "a": "We plan private trips, treks and tours in Nepal only, across nine regions from the Kathmandu Valley to the Far West. Each trip is built for one party, with licensed guides, the stays we name and transport that suits the route: private car, domestic flight, jeep or your own two feet."},
    {"q": "Are your prices fixed?",
     "a": "No. Prices on the site are indicative 'from' prices in US dollars per person, twin sharing, with a licensed guide and the stays named. The final price depends on dates, group size, flights and permits. We send a written quote with every line itemised before you pay anything."},
    {"q": "Can you change a trip on the site?",
     "a": "Yes, and most travellers do. The trips on the site are starting points that show what works on the ground. We add rest days, swap a trek for a jeep road, combine regions and send a new day-by-day plan with the sleeping height of every night."},
    {"q": "Do I need a guide to trek in Nepal?",
     "a": "Since April 2023 the Nepal Tourism Board has required foreign trekkers in national parks and conservation areas to trek with a licensed guide. The Khumbu municipality runs its own permit system and enforcement has varied. Restricted areas such as Upper Mustang and Manaslu always need a registered agency and guide. Check current status before you travel."},
    {"q": "When is the best time to visit Nepal?",
     "a": "For mountain views and trekking, October to mid-December and March to May. October and November bring the clearest air after the monsoon; spring brings rhododendrons and warmer high camps. The Terai parks are best from February to April. The monsoon, June to September, suits Upper Mustang, Dolpo and Limi, which sit in the rain shadow."},
    {"q": "Who will we deal with?",
     "a": "One planner handles your trip from the first message to the last transfer and is reachable on WhatsApp while you travel. On the ground, your guide carries a government licence and we brief them on your plan, pace and any health notes before you arrive."},
    {"q": "Where do your photos come from?",
     "a": "Every photo on this site comes from Wikimedia Commons under a free licence. We name the author and licence under each photo and list all of them, with links to the originals, on our photo credits page."},
    {"q": "Do you arrange permits and visas?",
     "a": "We arrange trekking and park permits, including restricted-area permits that only a registered agency can apply for, such as Upper Mustang, Manaslu and Kanchenjunga. Most nationalities can get a Nepal visa on arrival at Kathmandu; Indian citizens do not need one. Check current status before you travel."},
    {"q": "Is travel insurance included?",
     "a": "No. We ask every traveller to hold insurance that covers medical treatment and helicopter evacuation up to the highest altitude on their route. Many standard policies stop at 3,000 m or 4,000 m, so check the altitude limit before you buy."},
]


def ld(*items):
    """Render JSON-LD blocks safely."""
    return [json.dumps(i, ensure_ascii=False).replace("</", "<\\/") for i in items]


def crumbs(*pairs):
    items = [("Home", reverse("home"))] + list(pairs)
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": settings.SITE["url"] + u}
        for i, (n, u) in enumerate(items)]}
    return items, data


def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]}


def img_url(obj):
    imgs = obj.get("images") or []
    return imgs[0]["thumb"] if imgs else None


def org_ld():
    s = settings.SITE
    return {"@context": "https://schema.org", "@type": "TravelAgency", "name": s["name"], "url": s["url"],
            "areaServed": "Nepal"}


def _get(store, slug):
    obj = store.get(slug)
    if not obj:
        raise Http404
    return obj


def _month_now():
    return date.today().month - 1


# ---------------- home and indexes ----------------
def home(request):
    cat = catalogue()
    regions = list(cat.regions.values())
    featured = []
    for r in regions:
        if r["journeys"]:
            featured.append(sorted(r["journeys"], key=lambda j: -j.get("price_from_usd", 0))[len(r["journeys"]) // 2])
    # always a full row of four: top up with the grandest journeys not already shown
    for j in sorted(cat.journeys.values(), key=lambda j: -j.get("price_from_usd", 0)):
        if len(featured) % 4 == 0:
            break
        if j not in featured:
            featured.append(j)
    m = _month_now()
    in_season = [p for p in cat.places.values() if (p.get("best_months") or [0] * 12)[m] == 2]
    in_season = sorted(in_season, key=lambda p: (-len(p["journey_objs"]), p["name"]))[:8]
    fests = [f for f in cat.festivals.values() if (m + 1) in f.get("month_nums", []) or (m + 2) in f.get("month_nums", [])][:4]
    from .content import cross_section
    xs = cross_section()
    pick = {r: i for i, r in enumerate(["everest-khumbu", "kathmandu-valley", "chitwan-terai"])}
    hero_regions = sorted([r for r in regions if r["slug"] in pick], key=lambda r: pick[r["slug"]])
    day = date.today().toordinal()
    untold = cat.untold[day % max(1, len(cat.untold)):][:3] if cat.untold else []
    legend = cat.legends[day % len(cat.legends)] if cat.legends else None
    words = [w for w in cat.words if w.get("script")][day % 7::max(1, len(cat.words) // 6)][:5]
    xs_places = [{"n": p["name"], "a": p["altitude_m"], "u": p["url"]} for p in cat.places.values() if isinstance(p.get("altitude_m"), int)]
    return render(request, "yatra/home.html", {
        "regions": regions, "featured": featured[:8], "counts": cat.counts(), "month": MONTHS[m], "month_i": m,
        "in_season": in_season, "festivals": fests, "guides": list(cat.guides.values())[::9][:3],
        "themes": list(cat.themes.values())[:8], "months_short": MONTH_SHORT, "months_full": MONTHS,
        "posts": list(cat.posts.values())[:3], "hero_regions": hero_regions, "xs": xs,
        "xs_samples": json.dumps(xs["samples"]), "xs_places": json.dumps(xs_places).replace("</", "<\\/"),
        "xs_belts": json.dumps([[b[0], b[1], b[2], b[3]] for b in BELTS], ensure_ascii=False),
        "bs_now": BS_FOR_MONTH[m], "untold": untold, "legend": legend, "words": words,
        "ld": ld(org_ld(), {"@context": "https://schema.org", "@type": "WebSite", "name": settings.SITE["name"], "url": settings.SITE["url"]}),
    })


def lands(request):
    cat = catalogue()
    items, bc = crumbs(("Regions", reverse("lands")))
    return render(request, "yatra/lands.html", {"regions": list(cat.regions.values()), "crumbs": items,
                                                "months_short": MONTH_SHORT, "ld": ld(bc)})


def region(request, region):
    cat = catalogue()
    r = _get(cat.regions, region)
    items, bc = crumbs(("Regions", reverse("lands")), (r["name"], r["url"]))
    exps = [e for p in r["top_places"] for e in p.get("experiences", [])[:1]]
    styles = [cat.themes[t] for (rr, t) in cat.region_theme_pairs() if rr == region]
    months = [{"name": MONTHS[i], "slug": MONTHS[i].lower(), "rating": (r.get("best_months") or [0] * 12)[i],
               "weather": (r.get("months") or [{}] * 12)[i].get("weather", "") if i < len(r.get("months", [])) else ""}
              for i in range(12)]
    place_ld = {"@context": "https://schema.org", "@type": "TouristDestination", "name": r["name"],
                "description": r.get("summary"), "url": settings.SITE["url"] + r["url"],
                "includesAttraction": [{"@type": "TouristAttraction", "name": p["name"]} for p in r["places"]]}
    return render(request, "yatra/region.html", {
        "r": r, "crumbs": items, "experiences": exps, "styles": styles, "months": months,
        "kinds": [(k, KINDS[k][0]) for rr, k in cat.region_kind_pairs() if rr == region],
        "ld": ld(bc, place_ld, faq_ld(r.get("faqs", []))),
        "map_points": json.dumps([{"name": p["name"], "lat": p.get("lat"), "lng": p.get("lng"), "url": p["url"],
                                   "kind": p.get("kind", "")} for p in r["places"] if p.get("lat")]),
    })


def region_month(request, region, month):
    cat = catalogue()
    r = _get(cat.regions, region)
    names = [m.lower() for m in MONTHS]
    if month not in names:
        raise Http404
    i = names.index(month)
    md = r.get("months", [])[i] if i < len(r.get("months", [])) else {}
    go = [cat.places[s] for s in md.get("go", []) if s in cat.places]
    events = [cat.festivals[s] for s in md.get("events", []) if s in cat.festivals]
    journeys = [j for j in r["journeys"] if (j.get("best_months") or [0] * 12)[i] == 2]
    rating = (r.get("best_months") or [0] * 12)[i]
    others = [{"r": rr, "rating": (rr.get("best_months") or [0] * 12)[i]} for rr in cat.regions.values() if rr["slug"] != region]
    items, bc = crumbs(("Regions", reverse("lands")), (r["name"], r["url"]), (f"{MONTHS[i]}", request.path))
    title = f"{r['name']} in {MONTHS[i]}"
    faqs = [
        {"q": f"Is {MONTHS[i]} a good time to visit {r['name']}?",
         "a": (md.get("summary") or "")[:600] or f"See our month-by-month notes for {r['name']}."},
        {"q": f"What is the weather like in {r['name']} in {MONTHS[i]}?",
         "a": f"{md.get('weather', 'Weather varies across the region')}. Conditions change fast with altitude, so check the forecast for each stop a week before you travel."},
        {"q": f"Where should we go in {r['name']} in {MONTHS[i]}?",
         "a": ("We suggest " + ", ".join(p["name"] for p in go) + ". " if go else "") + (md.get("tip") or "")},
    ]
    return render(request, "yatra/region_month.html", {
        "r": r, "i": i, "month": MONTHS[i], "md": md, "go": go, "events": events, "journeys": journeys,
        "rating": rating, "others": others, "crumbs": items, "title": title, "faqs": faqs,
        "prev": names[(i - 1) % 12], "next": names[(i + 1) % 12], "prev_name": MONTHS[(i - 1) % 12], "next_name": MONTHS[(i + 1) % 12],
        "ld": ld(bc, faq_ld(faqs)),
    })


def region_theme(request, region, theme):
    cat = catalogue()
    r = _get(cat.regions, region)
    t = _get(cat.themes, theme)
    if (region, theme) not in cat.region_theme_pairs():
        raise Http404
    data = cat.theme_items(theme, region)
    items, bc = crumbs(("Regions", reverse("lands")), (r["name"], r["url"]), (t["name"], request.path))
    return render(request, "yatra/region_theme.html", {"r": r, "t": t, **data, "crumbs": items, "ld": ld(bc)})


def place(request, region, place):
    cat = catalogue()
    p = _get(cat.places, place)
    if p["region"] != region:
        return redirect(p["url"], permanent=True)
    r = p["region_obj"]
    items, bc = crumbs(("Regions", reverse("lands")), (r["name"], r["url"]), (p["name"], p["url"]))
    dest = {"@context": "https://schema.org", "@type": "TouristDestination", "name": p["name"],
            "description": p.get("summary"), "url": settings.SITE["url"] + p["url"], "image": img_url(p)}
    if p.get("lat"):
        dest["geo"] = {"@type": "GeoCoordinates", "latitude": p["lat"], "longitude": p["lng"]}
    return render(request, "yatra/place.html", {
        "p": p, "r": r, "crumbs": items, "ld": ld(bc, dest, faq_ld(p.get("faqs", []))),
        "map_points": json.dumps([{"name": x["name"], "lat": x.get("lat"), "lng": x.get("lng"), "url": x["url"], "main": x is p}
                                  for x in [p] + p["nearby_objs"] if x.get("lat")]),
    })


def experience(request, region, place, exp):
    cat = catalogue()
    e = _get(cat.experiences, exp)
    p = e["place_obj"]
    if p["slug"] != place or e["region"] != region:
        return redirect(e["url"], permanent=True)
    r = e["region_obj"]
    siblings = [x for x in p.get("experiences", []) if x is not e]
    items, bc = crumbs(("Regions", reverse("lands")), (r["name"], r["url"]), (p["name"], p["url"]), (e["title"], e["url"]))
    attraction = {"@context": "https://schema.org", "@type": "TouristAttraction", "name": e["title"],
                  "description": e.get("summary"), "image": img_url(e),
                  "containedInPlace": {"@type": "Place", "name": p["name"]}}
    return render(request, "yatra/experience.html", {
        "e": e, "p": p, "r": r, "siblings": siblings, "crumbs": items,
        "ld": ld(bc, attraction, faq_ld(e.get("faqs", []))),
    })


def journeys(request):
    cat = catalogue()
    items, bc = crumbs(("Trips", reverse("journeys")))
    return render(request, "yatra/journeys.html", {"journeys": list(cat.journeys.values()), "regions": list(cat.regions.values()),
                                                   "themes": list(cat.themes.values()), "crumbs": items, "ld": ld(bc)})


def journey(request, slug):
    cat = catalogue()
    j = _get(cat.journeys, slug)
    r = j["region_obj"]
    items, bc = crumbs(("Trips", reverse("journeys")), (j["title"], j["url"]))
    trip = {"@context": "https://schema.org", "@type": "TouristTrip", "name": j["title"], "description": j.get("summary"),
            "image": img_url(j), "touristType": [cat.themes[t]["name"] for t in j.get("themes", []) if t in cat.themes],
            "itinerary": {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "item": {"@type": "Place", "name": s["obj"]["name"]}}
                for i, s in enumerate(j["stop_objs"])]},
            "offers": {"@type": "Offer", "priceCurrency": "USD", "price": j.get("price_from_usd"),
                       "description": "Indicative price per person, twin sharing"}}
    related = [x for x in r["journeys"] if x is not j][:3]
    return render(request, "yatra/journey.html", {
        "j": j, "r": r, "crumbs": items, "related": related,
        "ld": ld(bc, trip, faq_ld(j.get("faqs", []))),
        "map_points": json.dumps([{"name": s["obj"]["name"], "lat": s["obj"].get("lat"), "lng": s["obj"].get("lng"),
                                   "url": s["obj"]["url"], "nights": s["nights"]} for s in j["stop_objs"] if s["obj"].get("lat")]),
    })


def stays(request):
    cat = catalogue()
    items, bc = crumbs(("Stays", reverse("stays")))
    return render(request, "yatra/stays.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def stay(request, slug):
    cat = catalogue()
    s = _get(cat.stays, slug)
    items, bc = crumbs(("Stays", reverse("stays")), (s["name"], s["url"]))
    hotel = {"@context": "https://schema.org", "@type": "Hotel", "name": s["name"], "description": s.get("summary"),
             "image": img_url(s), "address": {"@type": "PostalAddress", "addressLocality": (s.get("place_obj") or {}).get("name", "")}}
    if s.get("website"):
        hotel["sameAs"] = s["website"]
    others = [x for x in s["region_obj"]["stays"] if x is not s][:3]
    return render(request, "yatra/stay.html", {"s": s, "crumbs": items, "others": others,
                                               "ld": ld(bc, hotel, faq_ld(s.get("faqs", [])))})


def experiences(request):
    cat = catalogue()
    items, bc = crumbs(("Experiences", reverse("experiences")))
    kinds = sorted({e.get("kind", "") for e in cat.experiences.values() if e.get("kind")})
    return render(request, "yatra/experiences.html", {"regions": list(cat.regions.values()), "kinds": kinds,
                                                      "kind_links": [(k, v[0]) for k, v in KINDS.items()],
                                                      "count": len(cat.experiences), "crumbs": items, "ld": ld(bc)})


def _kind_page(request, kind, region=None):
    cat = catalogue()
    if kind not in KINDS:
        raise Http404
    name, tagline, intro, flag = KINDS[kind]
    exps = [e for e in cat.experiences.values() if e.get("kind") == kind and (region is None or e["region"] == region)]
    r = cat.regions.get(region) if region else None
    if region and (not r or (region, kind) not in cat.region_kind_pairs()):
        raise Http404
    trail = [("Experiences", reverse("experiences"))]
    if r:
        trail = [("Regions", reverse("lands")), (r["name"], r["url"]), (f"{name} experiences", request.path)]
    else:
        trail.append((name, request.path))
    items, bc = crumbs(*trail)
    lands = [cat.regions[rr] for rr, k in cat.region_kind_pairs() if k == kind]
    others = [(k, v[0]) for k, v in KINDS.items() if k != kind and (region is None or (region, k) in cat.region_kind_pairs())]
    return render(request, "yatra/experience_kind.html", {
        "kind": kind, "name": name, "tagline": tagline, "intro": intro, "exps": exps, "r": r,
        "lands": lands, "others": others, "crumbs": items, "ld": ld(bc)})


def experience_kind(request, kind):
    return _kind_page(request, kind)


def region_kind(request, region, kind):
    return _kind_page(request, kind, region)


def guides(request):
    cat = catalogue()
    items, bc = crumbs(("Guides", reverse("guides")))
    return render(request, "yatra/guides.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def guide(request, slug):
    cat = catalogue()
    g = _get(cat.guides, slug)
    r = g["region_obj"]
    items, bc = crumbs(("Guides", reverse("guides")), (g["title"], g["url"]))
    article = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g.get("summary"),
               "image": img_url(g), "author": {"@type": "Organization", "name": settings.SITE["byline"]},
               "publisher": {"@type": "Organization", "name": settings.SITE["name"]}}
    more = [x for x in r["guides"] if x is not g][:3]
    return render(request, "yatra/guide.html", {"g": g, "r": r, "crumbs": items, "more": more,
                                                "ld": ld(bc, article, faq_ld(g.get("faqs", [])))})


def festivals(request):
    cat = catalogue()
    items, bc = crumbs(("Festivals", reverse("festivals")))
    by_month = []
    for i, m in enumerate(MONTHS):
        fs = [f for f in cat.festivals.values() if (i + 1) in f.get("month_nums", [])]
        by_month.append({"name": m, "festivals": fs})
    return render(request, "yatra/festivals.html", {"by_month": by_month, "count": len(cat.festivals), "crumbs": items, "ld": ld(bc)})


def festival(request, slug):
    cat = catalogue()
    f = _get(cat.festivals, slug)
    items, bc = crumbs(("Festivals", reverse("festivals")), (f["name"], f["url"]))
    journeys = [j for j in f["region_obj"]["journeys"] if "festivals" in j.get("themes", [])][:3]
    return render(request, "yatra/festival.html", {"f": f, "crumbs": items, "journeys": journeys,
                                                   "bar": month_bar([2 if (i + 1) in f.get("month_nums", []) else 0 for i in range(12)]),
                                                   "ld": ld(bc, faq_ld(f.get("faqs", [])))})


def routes(request):
    cat = catalogue()
    items, bc = crumbs(("Routes", reverse("routes")))
    return render(request, "yatra/routes.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def route(request, slug):
    cat = catalogue()
    rt = _get(cat.routes, slug)
    if not (rt["from_obj"] and rt["to_obj"]):
        raise Http404
    items, bc = crumbs(("Routes", reverse("routes")), (f"{rt['from_obj']['name']} to {rt['to_obj']['name']}", rt["url"]))
    pts = [x for x in (rt["from_obj"], rt["to_obj"]) if x and x.get("lat")]
    return render(request, "yatra/route.html", {"rt": rt, "crumbs": items, "ld": ld(bc, faq_ld(rt.get("faqs", []))),
                                                "map_points": json.dumps([{"name": x["name"], "lat": x["lat"], "lng": x["lng"], "url": x["url"]} for x in pts])})


def themes(request):
    cat = catalogue()
    items, bc = crumbs(("Styles", reverse("themes")))
    rows = [{"t": t, "n": len(cat.theme_items(t["slug"])["journeys"])} for t in cat.themes.values()]
    return render(request, "yatra/themes.html", {"rows": rows, "crumbs": items, "ld": ld(bc)})


def theme(request, slug):
    cat = catalogue()
    t = _get(cat.themes, slug)
    data = cat.theme_items(slug)
    pairs = [cat.regions[r] for (r, tt) in cat.region_theme_pairs() if tt == slug]
    items, bc = crumbs(("Styles", reverse("themes")), (t["name"], t["url"]))
    return render(request, "yatra/theme.html", {"t": t, **data, "region_pages": pairs, "crumbs": items, "ld": ld(bc)})


def seasons(request):
    cat = catalogue()
    items, bc = crumbs(("Seasons", reverse("seasons")))
    return render(request, "yatra/seasons.html", {"regions": list(cat.regions.values()), "months": MONTHS,
                                                  "months_short": MONTH_SHORT, "crumbs": items, "ld": ld(bc)})


# ---------------- tools ----------------
def tools(request):
    items, bc = crumbs(("Trip tools", reverse("tools")))
    return render(request, "yatra/tools.html", {"crumbs": items, "ld": ld(bc)})


def tool_season(request):
    cat = catalogue()
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Season finder", reverse("tool_season")))
    data = [{"n": p["name"], "u": p["url"], "r": p["region_obj"]["name"], "rs": p["region"], "b": p.get("best_months") or [0] * 12,
             "k": p.get("kind", ""), "i": (p["images"][0]["thumb"] if p["images"] else "")} for p in cat.places.values()]
    return render(request, "yatra/tool_season.html", {"crumbs": items, "data": json.dumps(data).replace("</", "<\\/"), "months": MONTHS, "ld": ld(bc),
                                                      "regions": list(cat.regions.values()), "now": _month_now()})


def tool_budget(request):
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Budget builder", reverse("tool_budget")))
    return render(request, "yatra/tool_budget.html", {"crumbs": items, "ld": ld(bc), "regions": list(catalogue().regions.values())})


def tool_permits(request):
    cat = catalogue()
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Permits", reverse("tool_permits")))
    return render(request, "yatra/tool_permits.html", {"crumbs": items, "ld": ld(bc), "regions": list(cat.regions.values())})


# ---------------- enquiry ----------------
def plan(request):
    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("plan_thanks")
    else:
        initial = {"source_page": request.GET.get("from", "")[:300], "kind": "full"}
        if request.GET.get("land"):
            initial["lands"] = [request.GET["land"]]
        if request.GET.get("month") in MONTHS:
            initial["month"] = request.GET["month"]
        if request.GET.get("journey"):
            initial["message"] = f"I am interested in: {request.GET['journey'][:150]}"
        form = EnquiryForm(initial=initial)
    items, bc = crumbs(("Plan a trip", reverse("plan")))
    return render(request, "yatra/plan.html", {"form": form, "crumbs": items, "ld": ld(bc)})


def plan_thanks(request):
    return render(request, "yatra/plan_thanks.html", {"crumbs": crumbs(("Plan a trip", reverse("plan")))[0]})


# ---------------- static and utility ----------------
def old_policy(request, page):
    return redirect("policy", slug={"privacy": "privacy", "terms": "booking-terms"}[page], permanent=True)


def static_page(request, page):
    titles = {"about": "About us", "privacy": "Privacy", "terms": "Terms"}
    items, bc = crumbs((titles[page], request.path))
    return render(request, f"yatra/{page}.html", {"crumbs": items, "counts": catalogue().counts(), "ld": ld(bc)})


def faq(request):
    cat = catalogue()
    items, bc = crumbs(("FAQ", reverse("faq")))
    groups = [{"name": "Travelling with us", "faqs": COMPANY_FAQS}] + [
        {"name": r["name"], "faqs": r.get("faqs", []), "url": r["url"]} for r in cat.regions.values()]
    return render(request, "yatra/faq.html", {"groups": groups, "crumbs": items, "ld": ld(bc, faq_ld(COMPANY_FAQS))})


def photo_credits(request):
    cat = catalogue()
    items, bc = crumbs(("Photo credits", reverse("photo_credits")))
    return render(request, "yatra/photo_credits.html", {"images": cat.all_images(), "crumbs": items, "ld": ld(bc)})


def html_sitemap(request):
    cat = catalogue()
    items, bc = crumbs(("Sitemap", reverse("html_sitemap")))
    return render(request, "yatra/sitemap.html", {"cat": cat, "regions": list(cat.regions.values()), "crumbs": items,
                                                  "pairs": [(cat.regions[r], cat.themes[t]) for r, t in cat.region_theme_pairs()],
                                                  "kind_pairs": [(cat.regions[r], k, KINDS[k][0]) for r, k in cat.region_kind_pairs()],
                                                  "month_slugs": [(m, m.lower()) for m in MONTHS], "ld": ld(bc)})


def robots(request):
    body = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /plan/thank-you/\n\nSitemap: {settings.SITE['url']}/sitemap.xml\n"
    return HttpResponse(body, content_type="text/plain")


def llms(request):
    cat = catalogue()
    lines = [f"# {settings.SITE['name']}", "",
             "> Private trips, treks and tours in Nepal, told region by region with the stories, people and facts of each place.", ""]
    for r in cat.regions.values():
        lines.append(f"## {r['name']}")
        lines.append(f"- [{r['name']} overview]({settings.SITE['url']}{r['url']}): {r.get('summary', '')}")
        for p in r["places"]:
            lines.append(f"- [{p['name']}]({settings.SITE['url']}{p['url']}): {p.get('summary', '')}")
        for j in r["journeys"]:
            lines.append(f"- [{j['title']}]({settings.SITE['url']}{j['url']}): {j.get('summary', '')}")
        lines.append("")
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def not_found(request, exception=None):
    return render(request, "yatra/404.html", {"crumbs": []}, status=404)
