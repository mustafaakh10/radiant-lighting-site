from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Application, Category, Product


class StaticSitemap(Sitemap):
    priority = 1.0

    def items(self):
        return ["home", "catalogue:all"]

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


SITEMAPS = {"static": StaticSitemap, "categories": CategorySitemap, "spaces": SpaceSitemap, "products": ProductSitemap}
