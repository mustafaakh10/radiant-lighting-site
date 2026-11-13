from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Application, Category, Product


class StaticSitemap(Sitemap):
    priority = 1.0

    def items(self):
        return ["home", "catalogue:all", "rooms", "projects:list", "guides:list", "about", "contact"]

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    priority = 0.8

    def items(self):
        return Category.objects.all()


class SpaceSitemap(Sitemap):
    priority = 0.6

    def items(self):
        return Application.objects.all()


class ProductSitemap(Sitemap):
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_published=True).select_related("product_type__category")

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(Sitemap):
    priority = 0.5

    def items(self):
        from apps.projects.models import Project
        return Project.objects.filter(is_published=True)


class GuideSitemap(Sitemap):
    priority = 0.7

    def items(self):
        from apps.guides.models import Guide
        return Guide.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.lastmod


SITEMAPS = {"guides": GuideSitemap, "projects": ProjectSitemap, "static": StaticSitemap, "categories": CategorySitemap, "spaces": SpaceSitemap, "products": ProductSitemap}
