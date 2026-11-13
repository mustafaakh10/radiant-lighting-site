"""Guides: written advice articles that bring in search traffic and point to products. Edited in the Wagtail admin."""
import re

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from modelcluster.fields import ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.fields import RichTextField


class Guide(ClusterableModel):
    TOPICS = [("homes", "Homes"), ("shops", "Shops & offices"), ("buying", "Buying guides"), ("colour", "Colour & brightness")]
    title = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)
    topic = models.CharField(max_length=20, choices=TOPICS, default="buying")
    summary = models.CharField(max_length=220, help_text="One or two lines shown on cards and used as the intro.")
    body = RichTextField(features=["h2", "h3", "bold", "italic", "ol", "ul", "blockquote", "link", "hr"],
                         help_text="Use Heading 2 for sections. A quote block shows as a highlighted tip.")
    cover = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    seo_description = models.CharField("Search description", max_length=160, blank=True,
                                       help_text="Shown in Google results. Leave blank to use the summary. Aim for 140–160 characters.")
    products = ParentalManyToManyField("catalogue.Product", blank=True, related_name="guides", verbose_name="Products mentioned")
    published_on = models.DateField(default=timezone.localdate)
    updated_on = models.DateField(null=True, blank=True, help_text="Set when you revise the guide.")
    featured = models.BooleanField(default=False, help_text="Shown large at the top of the Guides page. The newest featured guide wins.")
    is_published = models.BooleanField(default=True)

    panels = [
        FieldPanel("title"), FieldPanel("slug"), FieldPanel("topic"), FieldPanel("summary"),
        FieldPanel("cover"), FieldPanel("body"), FieldPanel("products"),
        MultiFieldPanel([FieldPanel("seo_description")], "Search"),
        MultiFieldPanel([FieldRowPanel([FieldPanel("published_on"), FieldPanel("updated_on")]),
                         FieldRowPanel([FieldPanel("featured"), FieldPanel("is_published")])], "Display"),
    ]

    class Meta:
        ordering = ["-published_on", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("guides:detail", args=[self.slug])

    @property
    def description(self):
        return self.seo_description or self.summary

    @property
    def read_minutes(self):
        words = len(re.findall(r"\w+", strip_tags(self.body)))
        return max(1, round(words / 200))

    @property
    def lastmod(self):
        return self.updated_on or self.published_on
