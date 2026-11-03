from urllib.parse import quote

from django.http import HttpResponse
from django.shortcuts import render

from apps.catalogue.models import Application, Category
from apps.catalogue.views import published

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
    for fp in site.feature_products.all():
        seen = set()
        for v in fp.variants.select_related("image", "finish"):
            if v.label in seen:
                continue
            seen.add(v.label)
            feature_cards.append({"product": fp, "variant": v, "image": v.image or fp.cutout})

    return render(request, "core/home.html", {
        "site": site, "slides": site.slides.select_related("image"), "spaces": Application.objects.select_related("cutout", "photo"),
        "categories": categories, "feature_cards": feature_cards[:8], "range_total": len(products),
        "wa_trade": f"https://wa.me/{site.whatsapp}?text=" + quote("Hello Radiant Lighting, I'd like trade pricing for a project. I can share the BOQ / drawings."),
    })


def robots(request):
    lines = ["User-agent: *", "Disallow: /admin/", "Disallow: /search/", f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}"]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
