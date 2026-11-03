from django.core.management import call_command
from django.test import TestCase

from apps.catalogue.models import Product


class CatalogueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_catalogue", verbosity=0)

    def test_every_page_renders(self):
        urls = ["/", "/products/", "/products/new/", "/outdoor/", "/spaces/homes/", "/search/?q=strip", "/sitemap.xml", "/robots.txt"]
        urls += [p.get_absolute_url() for p in Product.objects.all()]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_category_filter(self):
        r = self.client.get("/products/profiles/")
        self.assertEqual(r.context["count"], 3)
        self.assertContains(r, "Straight Profiles")
        self.assertNotContains(r, "Rayzen Linear")

    def test_finish_and_type_filters_combine(self):
        r = self.client.get("/products/", {"type": "laser-blades", "finish": [str(Product.objects.get(slug="rayzen-linear").finishes.get(name="White").pk)]})
        names = {c["product"].name for c in r.context["cells"]}
        self.assertEqual(names, {"Rayzen Linear", "Rayzen Square"})

    def test_price_label(self):
        self.assertEqual(Product.objects.get(slug="straight-profiles").price_label, "From PKR 830")
        self.assertEqual(Product.objects.get(slug="opple-35").price_label, "Price on request")
        self.assertEqual(Product.objects.get(slug="phoenix").price_label, "PKR 4,699")

    def test_product_page_seo_and_whatsapp(self):
        r = self.client.get("/products/downlights/linea/")
        self.assertContains(r, '"@type": "Product"')
        self.assertContains(r, '"lowPrice": 700')
        self.assertContains(r, "https://wa.me/923412856432")
        self.assertContains(r, "<title>Linea · Laser Blades · Radiant Lighting</title>", html=False)

    def test_wrong_category_in_url_is_404(self):
        self.assertEqual(self.client.get("/products/profiles/linea/").status_code, 404)

    def test_unpublished_hidden(self):
        Product.objects.filter(slug="linea").update(is_published=False)
        self.assertEqual(self.client.get("/products/downlights/linea/").status_code, 404)
        self.assertNotContains(self.client.get("/products/"), ">Linea<")
