from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from apps.catalogue.sitemaps import SITEMAPS
from apps.core import views as core

urlpatterns = [
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", core.robots),
    path("", core.home, name="home"),
    path("", include("apps.catalogue.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [path("pages/", include(wagtail_urls))]
