"""Product catalogue. Everything here is editable in the Wagtail admin under Snippets."""
from django import forms
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.models import Orderable
from wagtail.search import index


class Sorted(models.Model):
    sort_order = models.PositiveIntegerField(default=0, help_text="Lower numbers come first.")

    class Meta:
        abstract = True
        ordering = ["sort_order", "pk"]


class Category(Sorted):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    cutout = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                               help_text="Product cut-out shown when there is no room photo.")
    photo = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                              help_text="Room photo for the homepage category grid (4:3, or 3:4 for the tall tile).")
    show_on_home = models.BooleanField(default=True)

    panels = [FieldPanel("name"), FieldPanel("slug"), FieldPanel("sort_order"), FieldPanel("show_on_home"),
              FieldRowPanel([FieldPanel("cutout"), FieldPanel("photo")])]

    class Meta(Sorted.Meta):
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalogue:category", args=[self.slug])


class ProductType(Sorted):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="types")
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)

    panels = [FieldPanel("category"), FieldPanel("name"), FieldPanel("slug"), FieldPanel("sort_order")]

    class Meta(Sorted.Meta):
        ordering = ["category__sort_order", "sort_order", "pk"]

    def __str__(self):
        return f"{self.category} · {self.name}"


class Application(Sorted):
    name = models.CharField(max_length=80, help_text="For example: Homes, Offices, Retail.")
    slug = models.SlugField(unique=True)
    cutout = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    photo = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                              help_text="Portrait room photo for 'Shop by space' (4:5).")

    panels = [FieldPanel("name"), FieldPanel("slug"), FieldPanel("sort_order"),
              FieldRowPanel([FieldPanel("cutout"), FieldPanel("photo")])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalogue:space", args=[self.slug])


class Finish(Sorted):
    name = models.CharField(max_length=40)
    swatch = models.CharField(max_length=7, default="#CCCCCC", help_text="Hex colour for the swatch, e.g. #1E1E1D.")

    panels = [FieldPanel("name"), FieldPanel("swatch"), FieldPanel("sort_order")]

    class Meta(Sorted.Meta):
        verbose_name_plural = "finishes"

    def __str__(self):
        return self.name


class ColourTemperature(Sorted):
    name = models.CharField(max_length=40, help_text="Filter label, e.g. Warm 3000K.")
    slug = models.SlugField(unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug"), FieldPanel("sort_order")]

    def __str__(self):
        return self.name


class Product(index.Indexed, ClusterableModel):
    INDOOR, OUTDOOR = "indoor", "outdoor"
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT, related_name="products")
    location = models.CharField(max_length=10, choices=[(INDOOR, "Indoor"), (OUTDOOR, "Outdoor")], default=INDOOR)
    short = models.CharField("Card line", max_length=120, help_text="One line under the name on product cards.")
    description = models.TextField()
    variant_label = models.CharField(max_length=30, default="Size", help_text="What the options are called, e.g. Wattage, Heads, Width.")
    warranty = models.CharField(max_length=80, blank=True)
    is_new = models.BooleanField("Show NEW badge", default=False)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    cutout = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                               help_text="Main product photo: square, light grey background, light switched on.")
    applications = ParentalManyToManyField(Application, blank=True, related_name="products")
    finishes = ParentalManyToManyField(Finish, blank=True, related_name="products", help_text="Used for filters and card swatches.")
    colour_temperatures = ParentalManyToManyField(ColourTemperature, blank=True, related_name="products")
    seo_description = models.CharField(max_length=160, blank=True, help_text="Google snippet. Leave blank to use the card line and description.")
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel([FieldPanel("name"), FieldPanel("slug"), FieldPanel("product_type"), FieldPanel("short"),
                         FieldPanel("description"), FieldRowPanel([FieldPanel("is_new"), FieldPanel("is_published"), FieldPanel("sort_order")])], "Product"),
        FieldPanel("cutout"),
        InlinePanel("gallery", label="More photos (installed shots, details)"),
        MultiFieldPanel([FieldPanel("variant_label"), InlinePanel("variants", label="Option", min_num=1)], "Sizes and prices"),
        InlinePanel("options", label="Extra choice (colour temperature, beam, type…)"),
        InlinePanel("specs", label="Specification row"),
        MultiFieldPanel([FieldPanel("location"), FieldPanel("applications", widget=forms.CheckboxSelectMultiple), FieldPanel("finishes", widget=forms.CheckboxSelectMultiple),
                         FieldPanel("colour_temperatures", widget=forms.CheckboxSelectMultiple)], "Filters"),
        MultiFieldPanel([FieldPanel("warranty"), FieldPanel("seo_description")], "Warranty and SEO"),
    ]
    search_fields = [index.SearchField("name", boost=3), index.SearchField("short"), index.SearchField("description"),
                     index.AutocompleteField("name"), index.FilterField("is_published")]

    class Meta:
        ordering = ["product_type__category__sort_order", "sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def category(self):
        return self.product_type.category

    def get_absolute_url(self):
        return reverse("catalogue:product", args=[self.category.slug, self.slug])

    def priced(self):
        return [v.price for v in self.variants.all() if v.price]

    @property
    def min_price(self):
        p = self.priced()
        return min(p) if p else None

    @property
    def max_price(self):
        p = self.priced()
        return max(p) if p else None

    @property
    def option_count(self):
        return len({v.label for v in self.variants.all()})

    @property
    def price_label(self):
        m = self.min_price
        if m is None:
            return "Price on request"
        many = self.option_count > 1 or len({v.price for v in self.variants.all() if v.price}) > 1
        return ("From " if many else "") + f"PKR {m:,}"


class Promo(Sorted):
    """A collection tile mixed into the unfiltered product grid, like a magazine break."""
    title = models.CharField(max_length=60)
    link_text = models.CharField(max_length=40, default="Shop the collection")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE, related_name="+")
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, related_name="+")
    position = models.PositiveIntegerField(default=6, help_text="Show after this many product cards.")
    photo = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                              help_text="Portrait mood photo (3:4). Without one, the product cut-out is shown on a dark background.")

    panels = [FieldPanel("title"), FieldPanel("link_text"), FieldRowPanel([FieldPanel("product"), FieldPanel("category")]),
              FieldRowPanel([FieldPanel("position"), FieldPanel("sort_order")]), FieldPanel("photo")]

    def __str__(self):
        return self.title

    def url(self):
        return self.product.get_absolute_url() if self.product else self.category.get_absolute_url() if self.category else reverse("catalogue:all")

    def cutout(self):
        if self.product and self.product.cutout:
            return self.product.cutout
        return self.category.cutout if self.category else None



class ProductVariant(Orderable):
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name="variants")
    label = models.CharField(max_length=60, help_text="e.g. 12W, 3 heads, 17mm. Repeat the same label once per finish when prices differ by finish.")
    finish = models.ForeignKey(Finish, null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                               help_text="Only when this price applies to one finish.")
    price = models.PositiveIntegerField("Price (PKR)", null=True, blank=True, help_text="Leave blank for 'Price on request'.")
    details = models.CharField(max_length=160, blank=True, help_text="e.g. 1,080 lm · 108×58 mm · cut-out Ø90–100 mm")
    model_no = models.CharField("Model number", max_length=60, blank=True)
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                              help_text="Only if this option looks different from the main photo.")
    is_default = models.BooleanField("Selected first", default=False)

    panels = [FieldRowPanel([FieldPanel("label"), FieldPanel("finish"), FieldPanel("price")]),
              FieldRowPanel([FieldPanel("details"), FieldPanel("model_no")]), FieldRowPanel([FieldPanel("image"), FieldPanel("is_default")])]

    def __str__(self):
        return f"{self.product} {self.label}" + (f" · {self.finish}" if self.finish else "")


class ProductOption(Orderable):
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name="options")
    name = models.CharField(max_length=40, help_text="e.g. Colour temperature, Beam, Type.")
    values = models.CharField(max_length=200, help_text="Comma-separated, e.g. 3000K, 4000K, 6000K")
    only_for = models.CharField(max_length=200, blank=True, help_text="Comma-separated option labels this applies to. Blank = all.")

    panels = [FieldRowPanel([FieldPanel("name"), FieldPanel("values")]), FieldPanel("only_for")]

    def value_list(self):
        return [v.strip() for v in self.values.split(",") if v.strip()]

    def only_list(self):
        return [v.strip() for v in self.only_for.split(",") if v.strip()]


class ProductSpec(Orderable):
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name="specs")
    label = models.CharField(max_length=60)
    value = models.CharField(max_length=160)

    panels = [FieldRowPanel([FieldPanel("label"), FieldPanel("value")])]


class ProductImage(Orderable):
    ROOM, DETAIL = "room", "detail"
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name="gallery")
    image = models.ForeignKey("wagtailimages.Image", on_delete=models.CASCADE, related_name="+")
    kind = models.CharField(max_length=10, choices=[(ROOM, "Installed / room photo"), (DETAIL, "Product detail")], default=ROOM)
    is_visualisation = models.BooleanField(default=False, help_text="Tick for AI or 3D renders, so they are not presented as real installations.")

    panels = [FieldRowPanel([FieldPanel("image"), FieldPanel("kind"), FieldPanel("is_visualisation")])]
