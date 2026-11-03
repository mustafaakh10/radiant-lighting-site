import json
from urllib.parse import quote

from django.db.models import Prefetch, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from apps.core.models import SiteContent

from .models import Application, Category, ColourTemperature, Finish, Product, ProductType, Promo, ProductVariant

SORTS = [("featured", "Featured"), ("new", "Newest"), ("low", "Price: low to high"), ("high", "Price: high to low"), ("name", "Name A–Z")]


def published():
    return (Product.objects.filter(is_published=True)
            .select_related("product_type__category", "cutout")
            .prefetch_related(Prefetch("variants", queryset=ProductVariant.objects.select_related("finish")),
                              "applications", "finishes", "colour_temperatures"))


def wa_link(number, text):
    return f"https://wa.me/{number}?text={quote(text)}"


def _facts(p):
    return {
        "category": {p.product_type.category.slug},
        "type": {p.product_type.slug},
        "location": {p.location},
        "space": {a.slug for a in p.applications.all()},
        "cct": {c.slug for c in p.colour_temperatures.all()},
        "finish": {str(f.pk) for f in p.finishes.all()},
    }


def _matches(facts, sel, skip=None):
    for group, chosen in sel.items():
        if not chosen or group == skip or (skip == "category" and group == "type"):
            continue
        if group == "category":
            if not (facts["category"] & chosen or facts["type"] & sel.get("type", set())):
                return False
        elif group == "type":
            if sel.get("category") and (facts["category"] & sel["category"]):
                continue
            if not facts["type"] & chosen:
                return False
        elif not facts[group] & chosen:
            return False
    return True


def catalogue(request, category=None, space=None, preset=None):
    groups = ["category", "type", "location", "space", "cct", "finish"]
    sel = {g: set(request.GET.getlist(g)) for g in groups}
    sort = request.GET.get("sort", "new" if preset == "new" else "featured")
    if category:
        get_object_or_404(Category, slug=category)
        sel["category"].add(category)
    if space:
        get_object_or_404(Application, slug=space)
        sel["space"].add(space)
    if preset == "outdoor":
        sel["location"].add(Product.OUTDOOR)

    products = list(published())
    facts = {p.pk: _facts(p) for p in products}
    shown = [p for p in products if _matches(facts[p.pk], sel)]
    if sort == "low":
        shown.sort(key=lambda p: (p.min_price is None, p.min_price or 0))
    elif sort == "high":
        shown.sort(key=lambda p: (p.max_price is None, -(p.max_price or 0)))
    elif sort == "name":
        shown.sort(key=lambda p: p.name.lower())
    elif sort == "new":
        shown.sort(key=lambda p: not p.is_new)

    def count(group, value):
        return sum(1 for p in products if value in facts[p.pk][group] and _matches(facts[p.pk], sel, skip=group))

    filters = {
        "category": [{"value": c.slug, "label": c.name, "n": count("category", c.slug), "on": c.slug in sel["category"],
                      "types": [{"value": t.slug, "label": t.name, "n": count("type", t.slug), "on": t.slug in sel["type"]} for t in c.types.all()]}
                     for c in Category.objects.prefetch_related("types")],
        "location": [{"value": v, "label": l, "n": count("location", v), "on": v in sel["location"]} for v, l in Product._meta.get_field("location").choices],
        "space": [{"value": a.slug, "label": a.name, "n": count("space", a.slug), "on": a.slug in sel["space"]} for a in Application.objects.all()],
        "cct": [{"value": c.slug, "label": c.name, "n": count("cct", c.slug), "on": c.slug in sel["cct"]} for c in ColourTemperature.objects.all()],
        "finish": [{"value": str(f.pk), "label": f.name, "swatch": f.swatch, "n": count("finish", str(f.pk)), "on": str(f.pk) in sel["finish"]} for f in Finish.objects.all()],
    }
    active = sum(len(v) for v in sel.values())

    cells = [{"product": p} for p in shown]
    if active == 0 and sort == "featured":
        for promo in Promo.objects.select_related("product__cutout", "category__cutout", "photo").order_by("-position"):
            cells.insert(min(promo.position, len(cells)), {"promo": promo})

    title = "All products"
    if active == 1:
        if sel["category"]:
            title = Category.objects.get(slug=next(iter(sel["category"]))).name
        elif sel["space"]:
            title = "Lighting for " + Application.objects.get(slug=next(iter(sel["space"]))).name.lower()
        elif sel["location"]:
            title = "Outdoor lighting" if Product.OUTDOOR in sel["location"] else "Indoor lighting"
    if preset == "new":
        title = "New in"

    return render(request, "catalogue/catalogue.html", {
        "title": title, "cells": cells, "count": len(shown), "total": len(products), "filters": filters,
        "active": active, "sort": sort, "sorts": SORTS, "action": request.path,
        "path_locked": {"category": category, "space": space, "location": Product.OUTDOOR if preset == "outdoor" else None},
    })


def _img(image, spec):
    return image.get_rendition(spec).url if image else ""


def product(request, category, slug):
    p = get_object_or_404(published(), slug=slug)
    if p.category.slug != category:
        raise Http404
    site = SiteContent.load(request_or_site=request)

    labels, by_label = [], {}
    default = None
    for v in p.variants.all():
        if v.label not in by_label:
            labels.append(v.label)
            by_label[v.label] = {"label": v.label, "details": v.details, "model": v.model_no, "prices": {}, "price": v.price,
                                 "image": _img(v.image, "max-1200x1200|format-webp") if v.image else ""}
        entry = by_label[v.label]
        if v.finish:
            entry["prices"][v.finish.name] = v.price
        if v.is_default and default is None:
            default = len(labels) - 1
    variants = [by_label[l] for l in labels]
    options = [{"name": o.name, "values": o.value_list(), "only": o.only_list()} for o in p.options.all()]
    swatches = {f.name: f.swatch for f in Finish.objects.all()}

    pics = []
    if p.cutout:
        pics.append({"kind": "cut", "src": _img(p.cutout, "max-1200x1200|format-webp"), "thumb": _img(p.cutout, "max-200x200|format-webp")})
    for v in p.variants.all():
        if v.image:
            src = _img(v.image, "max-1200x1200|format-webp")
            if all(x["src"] != src for x in pics):
                pics.append({"kind": "cut", "src": src, "thumb": _img(v.image, "max-200x200|format-webp"), "variant": v.label})
    for g in p.gallery.select_related("image"):
        pics.append({"kind": g.kind, "src": _img(g.image, "fill-1600x1600|format-webp"), "thumb": _img(g.image, "fill-200x200|format-webp"),
                     "render": g.is_visualisation})

    related = [x for x in published().filter(product_type__category=p.category).exclude(pk=p.pk)]
    related += [x for x in published().exclude(product_type__category=p.category).filter(applications__in=p.applications.all()).distinct() if x.cutout][: max(0, 8 - len(related))]

    data = {"name": p.name, "typeName": p.product_type.name, "variantLabel": p.variant_label, "variants": variants, "options": options, "default": default or 0,
            "swatches": swatches, "pics": pics, "wa": site.whatsapp, "fixedFinishes": [f.name for f in p.finishes.all()]}
    offers = p.priced()
    jsonld = {"@context": "https://schema.org", "@type": "Product", "name": p.name, "description": p.seo_description or p.description,
              "category": p.category.name, "brand": {"@type": "Brand", "name": "Radiant Lighting"},
              "image": [request.build_absolute_uri(x["src"]) for x in pics[:3]],
              "sku": next((v["model"] for v in variants if v["model"]), p.slug)}
    if offers:
        jsonld["offers"] = {"@type": "AggregateOffer", "priceCurrency": "PKR", "lowPrice": min(offers), "highPrice": max(offers),
                            "offerCount": len(variants), "availability": "https://schema.org/InStock",
                            "url": request.build_absolute_uri(p.get_absolute_url())}
    return render(request, "catalogue/product.html", {
        "p": p, "data": data, "jsonld": json.dumps(jsonld, ensure_ascii=False), "related": related[:8],
        "first": variants[data["default"]] if variants else None, "pics": pics,
        "wa_trade": wa_link(site.whatsapp, f"Hello Radiant Lighting, I'd like project / trade pricing for {p.name}."),
        "wa_datasheet": wa_link(site.whatsapp, f"Hello Radiant Lighting, please send the datasheet for {p.name}."),
        "wa_ies": wa_link(site.whatsapp, f"Hello Radiant Lighting, please send the IES file for {p.name}."),
    })


def _search(q):
    q = (q or "").strip()
    if not q:
        return Product.objects.none()
    cond = Q()
    for word in q.split():
        cond &= (Q(name__icontains=word) | Q(short__icontains=word) | Q(description__icontains=word)
                 | Q(product_type__name__icontains=word) | Q(variants__label__icontains=word) | Q(variants__details__icontains=word))
    return published().filter(cond).distinct()


def search(request):
    q = request.GET.get("q", "")
    return render(request, "catalogue/search.html", {"q": q, "results": list(_search(q))})


def suggest(request):
    q = request.GET.get("q", "")
    qs = _search(q)[:9] if q.strip() else published().filter(is_new=True)[:9]
    return JsonResponse({"results": [{"name": p.name, "short": p.short, "url": p.get_absolute_url(),
                                      "thumb": _img(p.cutout, "max-120x120|format-webp")} for p in qs]})
