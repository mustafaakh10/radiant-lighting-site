"""Projects (completed installations) and contact enquiries, both edited in the Wagtail admin."""
from django.db import models
from django.urls import reverse
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.models import Orderable


class Project(ClusterableModel):
    KINDS = [("home", "Home"), ("office", "Office"), ("retail", "Retail"), ("hospitality", "Hospitality"), ("outdoor", "Outdoor")]
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    kind = models.CharField("Type", max_length=20, choices=KINDS, default="home")
    city = models.CharField(max_length=60, default="Multan")
    year = models.PositiveIntegerField(null=True, blank=True)
    summary = models.CharField(max_length=200, help_text="One line, shown on the project card.")
    body = models.TextField(blank=True, help_text="A few short paragraphs. Leave a blank line between paragraphs.")
    cover = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    products = ParentalManyToManyField("catalogue.Product", blank=True, related_name="projects", verbose_name="Products used")
    featured = models.BooleanField("Show on homepage", default=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0, help_text="Lower numbers come first.")

    panels = [
        FieldPanel("title"), FieldPanel("slug"),
        FieldRowPanel([FieldPanel("kind"), FieldPanel("city"), FieldPanel("year")]),
        FieldPanel("summary"), FieldPanel("body"), FieldPanel("cover"),
        InlinePanel("photos", label="Gallery photo"),
        FieldPanel("products"),
        MultiFieldPanel([FieldRowPanel([FieldPanel("featured"), FieldPanel("is_published"), FieldPanel("sort_order")])], "Display"),
    ]

    class Meta:
        ordering = ["sort_order", "-year", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("projects:detail", args=[self.slug])

    def paragraphs(self):
        return [p.strip() for p in self.body.split("\n\n") if p.strip()]


class ProjectPhoto(Orderable):
    project = ParentalKey(Project, on_delete=models.CASCADE, related_name="photos")
    image = models.ForeignKey("wagtailimages.Image", on_delete=models.CASCADE, related_name="+")
    caption = models.CharField(max_length=120, blank=True)
    panels = [FieldPanel("image"), FieldPanel("caption")]


class Enquiry(models.Model):
    name = models.CharField(max_length=80)
    phone = models.CharField("Phone or WhatsApp", max_length=30)
    email = models.EmailField(blank=True)
    message = models.TextField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)
    handled = models.BooleanField(default=False)

    panels = [FieldPanel("name"), FieldPanel("phone"), FieldPanel("email"), FieldPanel("message"), FieldPanel("handled")]

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "enquiries"

    def __str__(self):
        return f"{self.name} · {self.created:%d %b %Y}"


SPACES = [
    ("Home", [("living", "Living room"), ("bedroom", "Bedroom"), ("kitchen", "Kitchen"), ("dining", "Dining"),
              ("bathroom", "Bathroom"), ("entrance", "Entrance & stairs"), ("home-outdoor", "Outdoor & facade")]),
    ("Commercial", [("office", "Office"), ("retail", "Shop & retail"), ("restaurant", "Restaurant & café"),
                    ("hotel", "Hotel & hospitality"), ("showroom", "Showroom & gallery"), ("facade", "Building facade")]),
]
SPACE_GROUP = {k: g for g, opts in SPACES for k, _ in opts}


class Room(ClusterableModel):
    """A styled room for the Shop the Room page, broken down into the lights that make it."""
    TONES = [(3000, "Warm 3000K"), (4000, "Neutral 4000K"), (6000, "Cool 6000K")]
    title = models.CharField(max_length=80, help_text="e.g. The Warm Living Room")
    slug = models.SlugField(unique=True)
    space = models.CharField(max_length=20, choices=SPACES, default="living")
    image = models.ForeignKey("wagtailimages.Image", on_delete=models.PROTECT, related_name="+",
                              help_text="Portrait photo, about 4:5. Mark each light with a numbered dot below.")
    tone = models.PositiveIntegerField("Light colour in the photo", choices=TONES, default=3000)
    why = models.TextField("Why it works", help_text="One or two sentences on how the lighting is laid out.")
    is_illustrative = models.BooleanField("AI or illustrative image", default=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("title"), FieldPanel("slug"),
        FieldRowPanel([FieldPanel("space"), FieldPanel("tone")]),
        FieldPanel("image"), FieldPanel("why"),
        InlinePanel("items", label="Light in this room", min_num=1),
        FieldRowPanel([FieldPanel("is_illustrative"), FieldPanel("is_published"), FieldPanel("sort_order")]),
    ]

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

    @property
    def group(self):
        return SPACE_GROUP.get(self.space, "Home")


class RoomItem(Orderable):
    room = ParentalKey(Room, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("catalogue.Product", on_delete=models.CASCADE, related_name="+")
    variant = models.ForeignKey("catalogue.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                                help_text="The size or wattage used. Its price is shown. Leave blank for 'Price on request'.")
    role = models.CharField("What it does here", max_length=60, help_text="e.g. Wall-washing spots")
    qty = models.PositiveIntegerField("Quantity", default=1)
    x = models.DecimalField("Dot across (%)", max_digits=5, decimal_places=1, default=50, help_text="0 = left edge, 100 = right edge")
    y = models.DecimalField("Dot down (%)", max_digits=5, decimal_places=1, default=50, help_text="0 = top, 100 = bottom")

    panels = [FieldRowPanel([FieldPanel("product"), FieldPanel("variant")]), FieldPanel("role"),
              FieldRowPanel([FieldPanel("qty"), FieldPanel("x"), FieldPanel("y")])]
