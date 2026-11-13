import json

from django.shortcuts import get_object_or_404, render

from .models import Guide


def guide_list(request):
    guides = Guide.objects.filter(is_published=True).select_related("cover")
    topic = request.GET.get("topic", "")
    topics = [(k, label) for k, label in Guide.TOPICS if guides.filter(topic=k).exists()]
    if topic:
        guides = guides.filter(topic=topic)
    guides = list(guides)
    featured = None if topic else next((g for g in guides if g.featured), None)
    rest = [g for g in guides if g is not featured]
    return render(request, "guides/list.html", {"featured": featured, "guides": rest, "topics": topics, "topic": topic, "nav": "guides"})


def guide_detail(request, slug):
    guide = get_object_or_404(Guide.objects.select_related("cover"), slug=slug, is_published=True)
    more = Guide.objects.filter(is_published=True).exclude(pk=guide.pk).select_related("cover")
    same = list(more.filter(topic=guide.topic)[:3])
    more = same + [g for g in more if g not in same][: 3 - len(same)]
    base = request.build_absolute_uri("/").rstrip("/")
    jsonld = {"@context": "https://schema.org", "@type": "Article", "headline": guide.title, "description": guide.description,
              "datePublished": guide.published_on.isoformat(), "dateModified": guide.lastmod.isoformat(),
              "author": {"@type": "Organization", "name": "Radiant Lighting"},
              "publisher": {"@type": "Organization", "name": "Radiant Lighting"},
              "mainEntityOfPage": base + guide.get_absolute_url()}
    return render(request, "guides/detail.html", {
        "guide": guide, "jsonld": json.dumps(jsonld, ensure_ascii=False), "more": more,
        "products": guide.products.filter(is_published=True).select_related("product_type__category", "cutout"),
        "nav": "guides"})
