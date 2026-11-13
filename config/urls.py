from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from apps.catalogue.sitemaps import SITEMAPS
from apps.core import deploy as core_deploy
from apps.core import views as core
from apps.projects import views as projects_views

urlpatterns = [
    path("_deploy/", core_deploy.deploy),
    path("_deploy/status/", core_deploy.status),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", core.robots),
    path("", core.home, name="home"),
    path("projects/", include("apps.projects.urls")),
    path("shop-the-room/", projects_views.rooms, name="rooms"),
    path("about/", projects_views.about, name="about"),
    path("contact/", projects_views.contact, name="contact"),
    path("", include("apps.catalogue.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.SERVE_MEDIA:
    # Test hosts with no web server in front (e.g. PythonAnywhere free) let Django serve uploads.
    from django.urls import re_path
    from django.views.static import serve
    urlpatterns += [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})]

urlpatterns += [path("pages/", include(wagtail_urls))]
