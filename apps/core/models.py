"""Site-wide content: contact details, homepage hero and feature, editable in Wagtail."""
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.models import Orderable


@register_setting(icon="cog")
class SiteContent(ClusterableModel, BaseGenericSetting):
    whatsapp = models.CharField("WhatsApp number (international, digits only)", max_length=20, default="923412856432")
    whatsapp_display = models.CharField(max_length=30, default="0341 2856432")
    email = models.EmailField(default="info@radiantlighting.pk")
    address = models.TextField(default="Office 6, 2nd Floor, Crystal Arcade\nLMQ Road, Multan")
    maps_query = models.CharField(max_length=120, default="Crystal Arcade LMQ Road Multan")

    intro_title = models.CharField(max_length=120, default="Architectural lighting, specified in Multan.")
    intro_text = models.TextField(default="Fifteen years of supplying homes, businesses and city projects, now with a range of our own.")

    feature_eyebrow = models.CharField(max_length=40, default="Just arrived")
    feature_title = models.CharField(max_length=80, default="Rayzen laser blades")
    feature_text = models.TextField(blank=True, default="")
    feature_products = models.ManyToManyField("catalogue.Product", blank=True, related_name="+",
                                              help_text="Products whose options appear as cards under the feature.")
    feature_image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    feature_link = models.ForeignKey("catalogue.Product", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    trade_title = models.CharField(max_length=120, default="Lighting a project? Send us the drawings.")
    trade_text = models.TextField(default="Contractors, architects and developers get project pricing, the right fitting for every space, and supply from one source, including Philips, Osram and NVC.")
    about_title = models.CharField(max_length=120, default="Fifteen years lighting Pakistan's homes, businesses and cities.")
    about_text = models.TextField(default="")
    showroom_image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    brands = models.CharField(max_length=200, default="PHILIPS, OSRAM, NVC", help_text="Comma-separated, shown as a row on the homepage. Leave blank to hide.")

    panels = [
        MultiFieldPanel([FieldRowPanel([FieldPanel("whatsapp"), FieldPanel("whatsapp_display")]), FieldPanel("email"),
                         FieldPanel("address"), FieldPanel("maps_query")], "Contact"),
        InlinePanel("slides", label="Hero slide", min_num=1, max_num=5),
        MultiFieldPanel([FieldPanel("intro_title"), FieldPanel("intro_text")], "Intro"),
        MultiFieldPanel([FieldPanel("feature_eyebrow"), FieldPanel("feature_title"), FieldPanel("feature_text"),
                         FieldPanel("feature_link"), FieldPanel("feature_products"), FieldPanel("feature_image")], "Feature"),
        MultiFieldPanel([FieldPanel("trade_title"), FieldPanel("trade_text")], "Commercial band"),
        MultiFieldPanel([FieldPanel("about_title"), FieldPanel("about_text"), FieldPanel("brands"), FieldPanel("showroom_image")], "About and showroom"),
    ]

    class Meta:
        verbose_name = "Site content"

    def brand_list(self):
        return [b.strip() for b in self.brands.split(",") if b.strip()]


class HeroSlide(Orderable):
    site = ParentalKey(SiteContent, on_delete=models.CASCADE, related_name="slides")
    title = models.CharField(max_length=80, help_text="Use a new line for a line break.")
    link_text = models.CharField(max_length=40)
    link_url = models.CharField(max_length=200, help_text="e.g. /products/downlights/ or /#commercial")
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                              help_text="Wide photo, about 2400×1100. Keep the left third calm for the headline.")
    fallback = models.CharField(max_length=12, default="warm", choices=[("warm", "Warm room"), ("cool", "Commercial"), ("studio", "Studio")],
                                help_text="Background used until a photo is added.")

    panels = [FieldRowPanel([FieldPanel("title"), FieldPanel("link_text"), FieldPanel("link_url")]), FieldRowPanel([FieldPanel("image"), FieldPanel("fallback")])]
