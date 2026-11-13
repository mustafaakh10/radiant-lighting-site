from django.conf import settings
from django.templatetags.static import static


def seo(request):
    """Canonical URL (no query string, fixed host) and defaults for social previews."""
    base = settings.SITE_URL or f"{request.scheme}://{request.get_host()}"
    return {
        "site_url": base,
        "canonical_url": base + request.path,
        "default_og_image": base + static("img/home/hero.webp"),
        "noindex": settings.SITE_NOINDEX,
    }
