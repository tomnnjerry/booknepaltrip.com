# Book Nepal Trip: content schema and house rules

Book Nepal Trip (booknepaltrip.com) plans private trips, treks and tours in Nepal only, across nine regions:
Kathmandu Valley, Pokhara & the Annapurnas, Everest & Solukhumbu, Chitwan & the Terai, Lumbini & the Buddha's
Country, Mustang & Dolpo, Langtang & Manaslu, Eastern Nepal, Far West & Karnali.
Byline: "Book Nepal Trip Desk". Voice: local, warm, exact, first person plural ("we"). We write like people who
grew up here and still walk these trails: names of tole and chowk, the festival that closes the road, the dish a
grandmother makes in that village. Audience: international and Indian travellers, first-timers to repeat trekkers.

The site is built on STORY: every place has a story, a legend (clearly labelled as legend), the people who live
there, local words, a dish, and lesser-known facts most travel sites never mention. Facts must be TRUE.
Lesser-known does not mean invented. If you are not sure, leave it out.

All content is JSON, UTF-8, under `content/<region-slug>/`. The JSON must parse (no comments, no trailing commas).
Slugs are lowercase-hyphenated ASCII and unique across the WHOLE site. The full list of place slugs, region slugs
and stay slugs is fixed in `content/_plan.json`: use those exact slugs.

## Writing rules (strict)

- Headings and titles: no full stop at the end; short, one line on desktop (≤ 60 characters).
- Plain and specific: numbers over adjectives (km, hours, metres, USD, NPR, months, °C, days).
- BANNED words/phrases: nestled, breathtaking, hidden gem, paradise, tapestry, embark, delve, unleash, vibrant,
  bustling, mesmerizing, stunning, magical, heaven on earth, a feast for the eyes, something for everyone,
  whether you're, look no further, ultimate guide, in this blog, in conclusion, unforgettable, world-class,
  seamless, elevate, immerse, timeless, boasts, roof of the world, land of contrasts, off the beaten path,
  Shangri-La. "iconic" and "curated" max once per file.
- No emoji. No exclamation marks.
- Facts that change (permits, TIMS/park fees, flight routes, road conditions, festival dates, trek closures,
  guide rules): state the rule as you understand it and add "check current status before you travel".
  Note: since April 2023 Nepal requires foreign trekkers in national parks and conservation areas to trek with a
  licensed guide (rule applied unevenly in Khumbu, where the local municipality runs its own permit): say so and
  add "check current status before you travel".
- Never invent reviews, awards, statistics, star ratings, founders, staff names, client counts, "since 19xx".
- Prices: indicative "from" USD per person, twin sharing, with licensed guide, the stays named and the transport
  listed. Round to the nearest 50. Realistic Nepal market prices (examples: Everest Base Camp 14 nights teahouse
  trek with guide and porter ≈ USD 1,450–1,900; Kathmandu–Pokhara–Chitwan 8 nights in good 4-star hotels ≈ USD
  1,250–1,800; Upper Mustang 14 nights with restricted permit USD 500 + ≈ USD 3,200–4,200).
- Stays: REAL, currently operating properties only. Do not invent amenities, room counts or awards.
- Distances/times realistic for Nepal roads ("Kathmandu–Pokhara ≈ 200 km · 6–8 h by road; 25 min by air").
- `best_months` is ALWAYS an array of 12 integers, Jan..Dec: 2 = best, 1 = good, 0 = avoid/closed.
- `wiki` = the EXACT title of an existing English Wikipedia article about that thing (used to fetch credited
  photos). Use "" if none exists. Do not guess.
- `image_query` = 3–6 words that would find a real photo of exactly that subject on Wikimedia Commons
  (e.g. "Nyatapola temple Bhaktapur", "Phewa lake Pokhara boats").
- `name_ne` = the name in Devanagari as Nepalis write it (e.g. "भक्तपुर"). Use "" if not certain.
- FAQs: real questions travellers search for; answers 40–90 words, answer first, specific.
- Altitudes in metres as integers. Sources: use well-established figures (Wikipedia-level).

## Story fields (used on every place, region and journey; these make the site different)

- `local_name`: older or community name with its language, e.g. "Yala (Nepal Bhasa)", "Khwopa (Nepal Bhasa)",
  "Khumbu (Sherpa)". "" if none.
- `story`: {"title": "≤ 60 chars, no full stop", "paras": ["80–140 words", "…", "…"]} — the history and life of
  the place told as narrative: who built it, what happened here, how people live now. Real history only.
- `legend`: 50–120 words. A folk legend or religious story connected to the place, clearly framed ("Local
  legend says…", "In the Swayambhu Purana…"). "" if none you know well.
- `people`: 40–90 words on the communities who live here (Newar, Tharu, Sherpa, Thakali, Gurung, Magar, Tamang,
  Loba, Maithil, Rai, Limbu, Khas, Dolpo-pa, etc.), their languages and livelihoods. Respectful and specific.
- `untold`: 3 lesser-known, verifiable facts: [{"fact": "25–60 words", "source": "where it can be checked, e.g.
  'Wikipedia: Nyatapola' or 'UNESCO World Heritage listing' or 'Department of Archaeology, Nepal'"}].
  Only facts you are highly confident are true. Never fake a source.
- `local_words`: 3 [{"word": "romanised", "script": "Devanagari or Tibetan script, '' if unsure",
  "lang": "Nepali | Nepal Bhasa | Sherpa | Tharu | Maithili | Tibetan | Gurung | Tamang | Thakali | Limbu | Doteli",
  "meaning": "≤ 20 words"}] — words a traveller will hear here.
- `taste`: {"name": "dish or drink", "text": "30–60 words: what it is, where to eat it here"}.

## Files to write for each region `<r>`

### 1. `content/<r>/region.json`
```json
{
  "slug": "kathmandu-valley", "name": "Kathmandu Valley", "name_ne": "काठमाडौं उपत्यका", "local_name": "Nepa (Nepal Bhasa)",
  "province": "Bagmati", "tagline": "≤ 8 words",
  "meta_description": "≤ 158 chars",
  "summary": "40–60 word answer-first summary",
  "intro": ["para (60–110 words)", "para", "para", "para"],
  "story": {"title": "…", "paras": ["…", "…", "…", "…"]},
  "legend": "…", "people": "…",
  "untold": [{"fact": "…", "source": "…"}],            // 5 for regions
  "local_words": [{"word": "…", "script": "…", "lang": "…", "meaning": "…"}],   // 5 for regions
  "taste": {"name": "…", "text": "…"},
  "facts": [["Best months", "Oct – Nov, Mar – Apr"], ["Gateway", "…"], ["Ideal length", "…"], ["Altitude range", "1,300 – 2,700 m"], ["Languages", "…"], ["Permits", "…"], ["Province", "Bagmati"]],
  "best_months": [1,1,2,2,1,0,0,0,1,2,2,1],
  "altitude_min_m": 1300, "altitude_max_m": 2732,
  "highlights": [{"title": "…", "text": "35–60 words"}],          // exactly 6
  "getting_there": "90–150 words",
  "permits": "60–120 words, or '' if none apply",
  "wiki": "Kathmandu Valley",
  "lat": 27.7, "lng": 85.33,
  "months": [                                                      // exactly 12, Jan..Dec
    {"month": "January", "rating": 1, "weather": "Kathmandu 2–19 °C, dry, clear mornings", "summary": "60–100 words",
     "go": ["place-slug", "place-slug", "place-slug"], "events": ["festival-slug"], "tip": "one sentence"}
  ],
  "faqs": [{"q": "…", "a": "…"}]                                    // exactly 9
}
```

### 2. `content/<r>/places/<place-slug>.json` (one file per place listed for your region in _plan.json)
```json
{
  "slug": "bhaktapur", "name": "Bhaktapur", "name_ne": "भक्तपुर", "local_name": "Khwopa (Nepal Bhasa)", "region": "kathmandu-valley",
  "kind": "city | old town | village | lake | viewpoint | national park | wildlife reserve | trek stop | base camp | pass | pilgrimage site | monastery | valley | hill town | archaeological site | tea country",
  "wiki": "Bhaktapur", "image_query": "Nyatapola temple Bhaktapur",
  "lat": 27.672, "lng": 85.428, "altitude_m": 1401,
  "tagline": "≤ 70 chars",
  "meta_description": "≤ 158 chars",
  "summary": "40–60 word answer-first summary",
  "intro": ["para 70–120 words", "para", "para"],
  "story": {"title": "…", "paras": ["…", "…", "…"]},
  "legend": "…", "people": "…",
  "untold": [{"fact": "…", "source": "…"}],                       // exactly 3
  "local_words": [{"word": "…", "script": "…", "lang": "…", "meaning": "…"}],   // exactly 3
  "taste": {"name": "Juju dhau", "text": "…"},
  "facts": [["Best months", "…"], ["Days we suggest", "2"], ["Nearest airport", "…"], ["From Kathmandu", "≈ 13 km · 45 min"], ["Altitude", "1,401 m"], ["Known for", "…"]],
  "best_months": [1,1,2,2,1,0,0,0,1,2,2,1],
  "nights": "1–2",
  "highlights": [{"title": "…", "text": "35–60 words"}],          // 5–6
  "how_to_reach": [{"mode": "Road", "text": "…"}, {"mode": "Air", "text": "…"}, {"mode": "On foot", "text": "…"}],   // 2–3 that apply
  "where_to_stay": "70–120 words naming areas and real properties (teahouses by village name are fine on treks)",
  "stays": ["stay-slug"],                                         // only slugs from _plan.json for this place; [] if none
  "tips": ["one sentence", "…"],                                   // 5
  "themes": ["heritage-and-temples", "food-and-festivals"],         // from THEMES below
  "nearby": ["place-slug"],                                        // 2–4 other places in this region
  "experiences": [                                                 // exactly 4
    {"slug": "bhaktapur-potters-square-wheel", "title": "≤ 55 chars", "kind": "heritage | spiritual | nature | wildlife | food | adventure | trek | water | craft | wellness",
     "duration": "2 hours", "best_time": "Morning, Oct–Apr",
     "image_query": "Bhaktapur pottery square", "wiki": "",
     "summary": "35–55 words", "body": ["para 70–120 words", "para", "para"],
     "good_for": ["couples", "families", "first-timers", "photographers", "solo", "seniors", "trekkers"],
     "faqs": [{"q": "…", "a": "…"}]}                                // exactly 3
  ],
  "faqs": [{"q": "…", "a": "…"}]                                    // exactly 9
}
```

### 3. `content/<r>/journeys/<journey-slug>.json` (count given in your task)
```json
{
  "slug": "everest-base-camp-trek-14n", "title": "≤ 50 chars", "region": "everest-khumbu",
  "kind": "trek | tour | wildlife | pilgrimage | culture | family | adventure | overland",
  "nights": 14, "themes": ["treks-and-trails", "high-altitude"],
  "grade": "Easy | Moderate | Challenging | Strenuous",
  "stops": [{"place": "lukla", "nights": 1}, {"place": "namche-bazaar", "nights": 2}],   // nights sum = nights; any place slug from _plan.json
  "start": "Kathmandu (Tribhuvan International Airport, KTM)", "end": "Kathmandu",
  "price_from_usd": 1650, "best_months": [0,0,2,2,1,0,0,0,1,2,2,1],
  "pace": "Unhurried | Balanced | Active", "max_altitude_m": 5545,
  "meta_description": "≤ 158 chars including 'N nights'",
  "summary": "40–60 words", "intro": ["para 70–120 words", "para"],
  "story": "80–140 words: the shape of the journey as a story — how the land, people and air change day by day",
  "highlights": ["…"],                                                          // 5
  "days": [{"day": 1, "title": "≤ 45 chars", "place": "place-slug or ''", "overnight": "Namche Bazaar", "alt_m": 3440,
            "move": "≈ 6 h walk · +800 m, or ≈ 200 km · 7 h drive, or ''", "text": "70–130 words", "meals": "Breakfast, Lunch, Dinner"}],  // days = nights + 1; alt_m = overnight altitude (last day: where it ends)
  "stays": ["stay-slug"],                                                       // from _plan.json, may be []
  "includes": ["…"], "excludes": ["…"],
  "good_to_know": ["…"],
  "faqs": [{"q": "…", "a": "…"}]                                                // exactly 9
}
```

### 4. `content/<r>/stays.json` — array, exactly the stays listed for your region in _plan.json
```json
[{"slug": "dwarikas-hotel-kathmandu", "name": "Dwarika's Hotel", "place": "kathmandu",
  "kind": "heritage hotel | boutique hotel | jungle lodge | mountain lodge | resort | eco-lodge | city hotel | homestay | farm stay",
  "wiki": "", "image_query": "Dwarika's Hotel Kathmandu courtyard",
  "summary": "35–55 words", "body": ["para 70–110 words", "para"],
  "why": ["one line", "one line", "one line"], "best_for": ["couples", "…"],
  "website": "",
  "faqs": [{"q": "…", "a": "…"}]}]                                                // exactly 3
```
If you cannot confirm a listed stay still operates, leave it out of stays.json (and out of place `stays`).

### 5. `content/<r>/guides/<guide-slug>.json` (count given in your task)
```json
{"slug": "kathmandu-valley-heritage-sites-guide", "title": "≤ 60 chars", "region": "kathmandu-valley",
 "category": "planning | seasons | trekking | culture | food | wildlife | practical | permits | stories",
 "meta_description": "≤ 158 chars", "summary": "40–60 words answer-first",
 "sections": [{"heading": "≤ 50 chars", "paras": ["…"], "list": ["optional"], "table": {"head": ["…"], "rows": [["…"]]}}],
 "related_places": ["place-slug"],
 "faqs": [{"q": "…", "a": "…"}]}                                                 // exactly 9
```
Guides: 1,100–1,600 words of body across 5–8 sections; use a table in at least one section.

### 6. `content/<r>/festivals.json` — array (3–4)
```json
[{"slug": "bisket-jatra", "name": "Bisket Jatra", "name_ne": "बिस्केट जात्रा", "place": "bhaktapur", "wiki": "Bisket Jatra",
  "image_query": "Bisket Jatra chariot Bhaktapur", "when": "Mid-April, around Nepali New Year (Baisakh 1)", "month_nums": [4],
  "summary": "35–55 words", "body": ["para 70–110 words", "para", "para"], "tips": ["…", "…", "…"],
  "faqs": [{"q": "…", "a": "…"}]}]                                                // exactly 4
```

### 7. `content/<r>/routes.json` — array (4): getting between two places
```json
[{"slug": "kathmandu-to-bhaktapur", "from": "kathmandu", "to": "bhaktapur", "distance_km": 13,
  "summary": "35–55 words",
  "options": [{"mode": "Private car", "time": "45 min", "text": "50–90 words"}, {"mode": "Local bus", "time": "…", "text": "…"}],
  "stops_on_way": ["…"], "tip": "one sentence",
  "faqs": [{"q": "…", "a": "…"}]}]                                                // exactly 4
```
`from` and `to` must be place slugs from _plan.json (`from` may be in another region, e.g. kathmandu).

## THEMES (use these slugs only)
treks-and-trails, high-altitude, heritage-and-temples, wildlife-and-jungle, spiritual-and-pilgrimage,
food-and-festivals, villages-and-homestays, lakes-and-rivers, family-trips, honeymoons, photography,
adventure-sports, crafts-and-makers, slow-and-wellness

## Cross-references
Place, stay and region slugs come only from `content/_plan.json`. Festival slugs in region `months[].events`
must exist in your own festivals.json.
