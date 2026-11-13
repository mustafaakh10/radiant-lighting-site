from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Enquiry, Project


class ProjectViewSet(SnippetViewSet):
    model = Project
    icon = "image"
    menu_label = "Projects"
    add_to_admin_menu = True
    list_display = ["title", "kind", "city", "year", "featured", "is_published"]
    list_filter = ["kind", "featured", "is_published"]


class EnquiryViewSet(SnippetViewSet):
    model = Enquiry
    icon = "mail"
    menu_label = "Enquiries"
    add_to_admin_menu = True
    list_display = ["name", "phone", "created", "handled"]
    list_filter = ["handled"]


register_snippet(ProjectViewSet)
register_snippet(EnquiryViewSet)


from .models import Room  # noqa: E402


class RoomViewSet(SnippetViewSet):
    model = Room
    icon = "image"
    menu_label = "Shop the room"
    add_to_admin_menu = True
    list_display = ["title", "space", "tone", "is_published"]
    list_filter = ["space", "is_published"]


register_snippet(RoomViewSet)
