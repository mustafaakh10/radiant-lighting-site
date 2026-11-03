def navigation(request):
    from .models import Application, Category
    return {
        "nav_categories": Category.objects.prefetch_related("types"),
        "nav_spaces": Application.objects.all(),
    }
