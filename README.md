# Radiant Lighting website

Django 5.1 + Wagtail 6.4. Products, sizes, prices, photos and homepage content are edited in the Wagtail admin at `/admin/`.

## Run it on your computer

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_catalogue        # loads the 23 ranges, photos and homepage text
python manage.py createsuperuser       # your admin login
python manage.py runserver
```

Open http://localhost:8000 for the site and http://localhost:8000/admin/ for the admin.

## Where things are edited

| What | Admin location |
|---|---|
| Products, sizes, prices, options, specs, photos | Snippets → Catalogue → Products |
| Categories, types, spaces, finishes, colour temperatures | Snippets → Catalogue |
| Collection tiles in the product grid | Snippets → Catalogue → Grid promos |
| Hero slides, intro, feature, trade band, about, contact, WhatsApp number | Settings → Site content |

Photos: upload in the product's **More photos** section. Tick **Visualisation** for AI or 3D renders, so they are labelled and never presented as real installations.

## URLs

- `/products/` with filters `?category=&type=&location=&space=&cct=&finish=&sort=`
- `/products/<category>/` and `/products/<category>/<product>/`
- `/spaces/<space>/`, `/outdoor/`, `/products/new/`, `/search/?q=`
- `/sitemap.xml`, `/robots.txt`. Product pages include Product schema (JSON-LD) with PKR prices.

## Deploy to a Hostinger VPS (Docker)

One-time setup on the server (Ubuntu with Docker installed):

```bash
git clone https://github.com/<you>/radiant-lighting-site.git ~/radiant-lighting-site
cd ~/radiant-lighting-site
cp .env.example .env && nano .env      # set domain, secret key, database password
docker compose up -d --build
docker compose exec web python manage.py seed_catalogue
docker compose exec web python manage.py createsuperuser
```

Point the domain's A records (`@` and `www`) at the VPS IP. Caddy gets the HTTPS certificate automatically.

### Automatic deploys

`.github/workflows/deploy.yml` runs the tests on every push to `main`, then deploys over SSH. To switch on deploys, add in the GitHub repo settings:

- Secrets: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` (a deploy key whose public half is in the server's `~/.ssh/authorized_keys`)
- Variable: `DEPLOY_ENABLED` = `true`

### Backups

```bash
docker compose exec db pg_dump -U radiant radiant > backup-$(date +%F).sql   # database
docker run --rm -v radiant-lighting-site_media:/m -v $PWD:/b alpine tar czf /b/media-$(date +%F).tgz -C /m .   # photos
```

## Tests

```bash
python manage.py test apps
```
