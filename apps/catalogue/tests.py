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


class SeoTests(TestCase):
    def test_robots_and_sitemap(self):
        r = self.client.get("/robots.txt")
        self.assertIn("Sitemap:", r.content.decode())
        self.assertIn("Disallow: /admin/", r.content.decode())
        with self.settings(SITE_NOINDEX=True):
            self.assertIn("Disallow: /\n", self.client.get("/robots.txt").content.decode())
        x = self.client.get("/sitemap.xml").content.decode()
        for path in ("/about/", "/contact/", "/projects/", "/shop-the-room/"):
            self.assertIn(path, x)

    def test_canonical_drops_query_and_search_noindex(self):
        html = self.client.get("/products/?location=indoor").content.decode()
        self.assertIn('rel="canonical" href="http://testserver/products/"', html)
        self.assertIn('property="og:image"', html)
        self.assertIn("noindex", self.client.get("/search/?q=x").content.decode())
        with self.settings(SITE_URL="https://radiantlighting.pk"):
            self.assertIn('href="https://radiantlighting.pk/about/"', self.client.get("/about/").content.decode())


class GuideTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_catalogue", verbosity=0)
        call_command("seed_guides", verbosity=0)

    def test_guide_pages_and_links(self):
        from apps.guides.models import Guide
        self.assertEqual(self.client.get("/guides/").status_code, 200)
        self.assertEqual(self.client.get("/guides/?topic=buying").status_code, 200)
        g = Guide.objects.get(slug="how-many-downlights-per-room")
        html = self.client.get(g.get_absolute_url()).content.decode()
        self.assertIn('"@type": "Article"', html)
        self.assertIn("Products mentioned", html)
        self.assertIn("/guides/", self.client.get("/").content.decode())
        self.assertIn("/guides/how-many-downlights-per-room/", self.client.get("/sitemap.xml").content.decode())
        p = g.products.first()
        self.assertIn("Helpful guides", self.client.get(p.get_absolute_url()).content.decode())
        self.assertIn("Helpful guides", self.client.get(p.category.get_absolute_url()).content.decode())

    def test_unpublished_guide_hidden(self):
        from apps.guides.models import Guide
        Guide.objects.filter(slug="lighting-a-shop").update(is_published=False)
        self.assertEqual(self.client.get("/guides/lighting-a-shop/").status_code, 404)
