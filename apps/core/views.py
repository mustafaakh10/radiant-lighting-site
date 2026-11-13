from urllib.parse import quote

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from apps.catalogue.models import Application, Category
from apps.catalogue.views import published

from apps.projects.models import Project

from .models import SiteContent


def home(request):
    site = SiteContent.load(request_or_site=request)
    products = list(published())
    count = {}
    for p in products:
        count[p.product_type.category_id] = count.get(p.product_type.category_id, 0) + 1
    categories = [c for c in Category.objects.filter(show_on_home=True).select_related("cutout", "photo")][:5]
    for c in categories:
        c.range_count = count.get(c.pk, 0)

    feature_cards = []
    chosen = list(site.feature_products.all())
    if chosen:
        for fp in chosen:
            seen = set()
            for v in fp.variants.select_related("image", "finish"):
                if v.label in seen:
                    continue
                seen.add(v.label)
                feature_cards.append({"url": fp.get_absolute_url(), "name": f"{fp.name} {v.label}", "image": v.image or fp.cutout,
                                      "price": f"PKR {v.price:,}" if v.price else "Price on request", "is_new": fp.is_new, "finishes": fp.finishes.all()})
    else:
        for fp in [p for p in products if p.is_new]:
            feature_cards.append({"url": fp.get_absolute_url(), "name": fp.name, "image": fp.cutout, "price": fp.price_label,
                                  "is_new": True, "finishes": fp.finishes.all()})

    blurbs = {"homes": "Living rooms, kitchens and bedrooms", "offices": "Even, low-glare light to work under",
              "retail": "Track and accent light for displays", "hospitality": "Warm, dimmable light for guests",
              "outdoor-facades": "IP65 wall, step and garden lights"}
    spaces = list(Application.objects.all())
    for a in spaces:
        a.blurb = blurbs.get(a.slug, "")
    by_slug = {c.slug: c.get_absolute_url() for c in Category.objects.all()}
    all_url = reverse("catalogue:all")
    return render(request, "core/home.html", {
        "link_cob": by_slug.get("downlights", all_url), "link_track": by_slug.get("track-lights", all_url),
        "link_blade": reverse("catalogue:search") + "?q=laser+blade",
        "wa_project": f"https://wa.me/{site.whatsapp}?text=" + quote("Hello Radiant Lighting, I need lighting for a space."),
        "work_projects": Project.objects.filter(is_published=True, featured=True).select_related("cover")[:3],
        "site": site, "slides": site.slides.select_related("image"), "spaces": spaces,
        "categories": categories, "feature_cards": feature_cards[:8], "range_total": len(products),
        "wa_trade": f"https://wa.me/{site.whatsapp}?text=" + quote("Hello Radiant Lighting, I'd like trade pricing for a project. I can share the BOQ / drawings."),
    })


def robots(request):
    if settings.SITE_NOINDEX:
        lines = ["User-agent: *", "Disallow: /"]
    else:
        base = settings.SITE_URL or f"{request.scheme}://{request.get_host()}"
        lines = ["User-agent: *", "Disallow: /admin/", "Disallow: /search/", "Disallow: /_deploy/", f"Sitemap: {base}/sitemap.xml"]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
