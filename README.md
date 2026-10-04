# Book Nepal Trip

booknepaltrip.com: private trips, treks and tours in Nepal, told region by region. A Django 5 site whose pages are
all rendered from the JSON files in `content/` (9 regions, 109 places, ~100 trips, guides, festivals, routes and
stays). Enquiries and newsletter sign-ups are stored in a small SQLite database and managed in `/admin/`.

## Run it locally

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser      # for /admin/, where enquiries arrive
python manage.py runserver            # http://127.0.0.1:8000
```

With `DJANGO_DEBUG=1` (the default) content edits show on refresh.

## Checks before you deploy

```bash
python tools/smoke.py                          # renders every URL in the sitemap; expect "0 failures"
python tools/check_region.py <region-slug>     # validates a region's JSON against content/SCHEMA.md
```

## Deploy (any Linux server with Python 3.11+)

```bash
pip install -r requirements.txt
export DJANGO_DEBUG=0 DJANGO_SECRET_KEY='<long random string>'
python manage.py migrate
python manage.py collectstatic --noinput
BNT_HASHED_STATIC=1 gunicorn bnt.wsgi --bind 127.0.0.1:8000 --workers 3
```

Put nginx (or Caddy) in front for HTTPS and forward `X-Forwarded-Proto`. WhiteNoise serves `/static/`, so no
separate static location is needed. Back up `db.sqlite3` (or set `BNT_DB_PATH` to a backed-up location).
A platform such as Railway, Render or Fly.io works too: use the gunicorn line as the start command and a
persistent volume for the database.

## Settings (environment variables)

| Variable | What it does |
|---|---|
| `DJANGO_DEBUG` | `0` in production |
| `DJANGO_SECRET_KEY` | Required when `DJANGO_DEBUG=0` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated; defaults to booknepaltrip.com, www, localhost |
| `BNT_HASHED_STATIC` | `1` after `collectstatic`, for cache-busting file names |
| `BNT_EMAIL` | Public email shown across the site |
| `BNT_PHONE` | Phone as displayed, e.g. `+977 980-0000000` (call buttons appear when set) |
| `BNT_WHATSAPP` | Digits with country code, e.g. `9779800000000` (WhatsApp buttons appear when set) |
| `BNT_ADDRESS` | Office address in the footer, About and Contact pages |
| `BNT_HOURS` | Office hours line in the contact panel |
| `BNT_LICENCE`, `BNT_MEMBERSHIPS`, `BNT_PAYMENTS` | Trust line in the footer (hidden while empty) |
| `BNT_GA4` | Google Analytics 4 ID; nothing loads while empty (add a consent banner if you set it) |
| `BNT_NOTIFY_EMAIL` | Where new enquiries are emailed (comma-separated) |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` | SMTP for those emails |
| `BNT_DB_PATH` | SQLite file location |

## Before launch: what only the business can supply

1. Contact details: `BNT_EMAIL`, `BNT_PHONE`, `BNT_WHATSAPP`, `BNT_ADDRESS`.
2. Licence and memberships for the footer: `BNT_LICENCE`, `BNT_MEMBERSHIPS`.
3. Policies in `yatra/policies.py`: every `[BRACKETED]` value (legal name, registration, PAN/VAT, deposit
   percentages, cancellation scale, payment methods, review date) needs your figures and a legal review.
4. Facts the writers flagged: `content/FACTS_TO_CONFIRM.md`.
5. Photos: `content/images.json` is built by `python tools/fetch_images.py` (Wikimedia Commons, credited on
   every page and at `/photo-credits/`). Re-run it after adding places; use `--force` to refetch.

## Where things live

- `content/` JSON content, `content/SCHEMA.md` the writing rules and schema
- `yatra/content.py` builds the in-memory catalogue; `yatra/views.py`, `yatra/views_more.py` the pages
- `templates/yatra/` templates; `static/css/lokta.css` and `static/js/lokta.js` the front end
- `yatra/atlas.py` draws the SVG maps from `content/outlines.json` (Natural Earth, Nepal's point of view)
- `tools/` build and check scripts
