from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Guide


class GuideViewSet(SnippetViewSet):
    model = Guide
    icon = "doc-full"
    menu_label = "Guides"
    add_to_admin_menu = True
    list_display = ["title", "topic", "published_on", "featured", "is_published"]
    list_filter = ["topic", "featured", "is_published"]


register_snippet(GuideViewSet)
