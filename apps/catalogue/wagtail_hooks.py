from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import Application, Category, ColourTemperature, Finish, Product, ProductType, Promo


class ProductViewSet(SnippetViewSet):
    model = Product
    icon = "pick"
    menu_label = "Products"
    list_display = ["name", "product_type", "price_label", "is_new", "is_published"]
    list_filter = ["product_type__category", "is_new", "is_published", "location"]
    search_fields = ["name", "short"]
    ordering = ["product_type__category__sort_order", "sort_order", "name"]


class CategoryViewSet(SnippetViewSet):
    model = Category
    icon = "folder-open-inverse"
    list_display = ["name", "slug", "sort_order", "show_on_home"]


class TypeViewSet(SnippetViewSet):
    model = ProductType
    icon = "list-ul"
    menu_label = "Types"
    list_display = ["name", "category", "sort_order"]
    list_filter = ["category"]


class ApplicationViewSet(SnippetViewSet):
    model = Application
    icon = "home"
    menu_label = "Spaces"
    list_display = ["name", "slug", "sort_order"]


class FinishViewSet(SnippetViewSet):
    model = Finish
    icon = "image"


class CCTViewSet(SnippetViewSet):
    model = ColourTemperature
    icon = "time"
    menu_label = "Colour temperatures"


class PromoViewSet(SnippetViewSet):
    model = Promo
    icon = "image"
    menu_label = "Grid promos"
    list_display = ["title", "position"]


class CatalogueGroup(SnippetViewSetGroup):
    menu_label = "Catalogue"
    menu_icon = "pick"
    menu_order = 100
    items = (ProductViewSet, CategoryViewSet, TypeViewSet, ApplicationViewSet, FinishViewSet, CCTViewSet, PromoViewSet)


register_snippet(CatalogueGroup)
