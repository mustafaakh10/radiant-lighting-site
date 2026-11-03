"""Load the starting catalogue (23 ranges) and homepage content.

    python manage.py seed_catalogue           # first run on an empty database
    python manage.py seed_catalogue --reset   # wipe catalogue tables and load again

Safe to re-run: existing products (matched by slug) are left alone unless --reset is given.
"""
import json
from pathlib import Path

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from wagtail.images.models import Image
from wagtail.models import Site

from apps.catalogue.models import (Application, Category, ColourTemperature, Finish, Product, ProductOption, ProductSpec,
                                   ProductType, ProductVariant, Promo)
from apps.core.models import HeroSlide, SiteContent

SEED = Path(__file__).resolve().parents[2] / "seed"

APPS = [("homes", "Homes", "home", "tulip"), ("offices", "Offices", "office", "rayzen-linear"), ("retail", "Retail", "retail", "track-decor"),
        ("hospitality", "Hospitality", "hospitality", "linea-3"), ("outdoor-facades", "Outdoor & facades", "outdoor", "trail")]
CCTS = [("warm", "Warm 3000K"), ("neutral", "Neutral 4000K"), ("cool", "Cool 6000K"), ("tunable", "Tunable white"), ("colour", "Colour / RGB")]
FINISHES = [("White", "#F2F0EB"), ("Black", "#1E1E1D"), ("Silver", "#C8CBCE")]
ABOUT = ("Radiant Lighting is led by Mohammad Akhtar, who worked with Philips, Signify and GE Lighting on projects from the GCC to "
         "Europe before bringing that experience home to Multan. Today we distribute Philips, Osram and NVC, supply commercial, "
         "industrial and infrastructure projects, and design a range of our own.")
RAYZEN = ("Crisp, high colour-rendering light (CRI above 90) with a tight 24° beam. Linear runs from 3W to 30W and square grilles "
          "up to 32W, in white or black.")


class Command(BaseCommand):
    help = "Load the starting Radiant Lighting catalogue and homepage content."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete catalogue data first.")

    def image(self, name, title=None):
        if not name:
            return None
        found = Image.objects.filter(title=title or name).first()
        if found:
            return found
        path = SEED / "img" / f"{name}.webp"
        if not path.exists():
            self.stderr.write(f"  missing image {path.name}")
            return None
        with path.open("rb") as fh:
            img = Image(title=title or name)
            img.file.save(path.name, ImageFile(fh, name=path.name), save=False)
            img.save()
        return img

    @transaction.atomic
    def handle(self, *args, reset=False, **opts):
        data = json.loads((SEED / "products.json").read_text())
        if reset:
            for m in (Promo, ProductVariant, ProductOption, ProductSpec, Product, ProductType, Category, Application, ColourTemperature, Finish):
                m.objects.all().delete()

        finishes = {n: Finish.objects.get_or_create(name=n, defaults={"swatch": c, "sort_order": i})[0] for i, (n, c) in enumerate(FINISHES)}
        ccts = {s: ColourTemperature.objects.get_or_create(slug=s, defaults={"name": n, "sort_order": i})[0] for i, (s, n) in enumerate(CCTS)}
        apps = {}
        for i, (slug, name, key, img) in enumerate(APPS):
            a, made = Application.objects.get_or_create(slug=slug, defaults={"name": name, "sort_order": i})
            if made or not a.cutout:
                a.cutout = self.image(img); a.save()
            apps[key] = a

        cats, types = {}, {}
        for i, c in enumerate(data["categories"]):
            cat, made = Category.objects.get_or_create(slug=c["id"], defaults={"name": c["label"], "sort_order": i,
                                                                               "show_on_home": c["id"] != "power-accessories"})
            if made or not cat.cutout:
                cat.cutout = self.image(c["img"]); cat.save()
            cats[c["id"]] = cat
            for j, sub in enumerate(c["subs"]):
                types[sub] = ProductType.objects.get_or_create(slug=slugify(sub), defaults={"name": sub, "category": cat, "sort_order": j})[0]

        made_n = 0
        for i, p in enumerate(data["products"]):
            if Product.objects.filter(slug=p["id"]).exists():
                continue
            prod = Product(name=p["name"], slug=p["id"], product_type=types[p["sub"]], location=p.get("loc") or "indoor",
                           short=p["short"], description=p["desc"], variant_label=p["vlabel"], warranty=p.get("warranty", ""),
                           is_new=bool(p.get("isNew")), sort_order=i, cutout=self.image(p.get("img")))
            prod.save()
            prod.applications.set([apps[a] for a in p.get("app", []) if a in apps])
            prod.finishes.set([finishes[f] for f in p.get("fin", []) if f in finishes])
            prod.colour_temperatures.set([ccts[c] for c in p.get("cct", []) if c in ccts])
            prod.save()  # ParentalManyToManyField values are only written on save
            default = p.get("def", 0)
            k = 0
            for vi, v in enumerate(p["v"]):
                label, price, details = v[0], v[1], v[2] if len(v) > 2 else ""
                model = v[3] if len(v) > 3 else ""
                img = self.image(v[4]) if len(v) > 4 and v[4] else None
                rows = price.items() if isinstance(price, dict) else [(None, price)]
                for fin, amount in rows:
                    ProductVariant.objects.create(product=prod, label=label, finish=finishes.get(fin) if fin else None,
                                                  price=amount or None, details=details, model_no=model, image=img,
                                                  is_default=(vi == default and k == 0), sort_order=k)
                    k += 1
            only = []
            if p.get("optsFor"):
                only = [p["v"][n][0] for n in p["optsFor"]]
            for oi, (name, values) in enumerate(p.get("opts", [])):
                ProductOption.objects.create(product=prod, name=name, values=", ".join(values), only_for=", ".join(only), sort_order=oi)
            for si, (label, value) in enumerate(p.get("base", [])):
                ProductSpec.objects.create(product=prod, label=label, value=value, sort_order=si)
            made_n += 1

        if not Promo.objects.exists():
            Promo.objects.create(title="The Linea collection", link_text="Shop Linea", product=Product.objects.get(slug="linea"), position=5)
            Promo.objects.create(title="Strip & profile systems", link_text="Shop profiles", category=cats["profiles"], position=13, sort_order=1)

        site = SiteContent.load(request_or_site=Site.objects.get(is_default_site=True))
        if not site.about_text:
            site.about_text = ABOUT
        if not site.feature_text:
            site.feature_text = RAYZEN
        site.feature_link = site.feature_link or Product.objects.filter(slug="rayzen-linear").first()
        site.save()
        site.feature_products.set(Product.objects.filter(slug__in=["rayzen-linear", "rayzen-square"]))
        if not site.slides.exists():
            for i, (title, text, url, fb) in enumerate([("Lighting for\nmodern homes", "Shop residential", "/spaces/homes/", "warm"),
                                                         ("Specified for\ncommercial projects", "Get trade pricing", "/#commercial", "cool"),
                                                         ("Rayzen\nlaser blades", "Explore Rayzen", "/products/downlights/rayzen-linear/", "studio")]):
                HeroSlide.objects.create(site=site, title=title, link_text=text, link_url=url, fallback=fb, sort_order=i)
        self.stdout.write(self.style.SUCCESS(f"Loaded {made_n} new product ranges ({Product.objects.count()} in total)."))
