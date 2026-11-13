from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.models import SiteContent

from .forms import EnquiryForm
from .models import Project


def project_list(request):
    projects = Project.objects.filter(is_published=True).select_related("cover")
    kind = request.GET.get("type", "")
    kinds = [(k, label) for k, label in Project.KINDS if projects.filter(kind=k).exists()]
    if kind:
        projects = projects.filter(kind=kind)
    return render(request, "projects/list.html", {"projects": projects, "kinds": kinds, "kind": kind, "nav": "projects"})


def project_detail(request, slug):
    project = get_object_or_404(Project.objects.select_related("cover"), slug=slug, is_published=True)
    more = Project.objects.filter(is_published=True).exclude(pk=project.pk).select_related("cover")[:3]
    return render(request, "projects/detail.html", {
        "project": project, "photos": project.photos.select_related("image"),
        "products": project.products.filter(is_published=True).select_related("product_type__category", "cutout"),
        "more": more, "nav": "projects"})


def about(request):
    from apps.catalogue.views import published
    return render(request, "core/about.html", {
        "projects": Project.objects.filter(is_published=True).select_related("cover")[:3],
        "range_total": published().count(), "nav": "about"})


def contact(request):
    site = SiteContent.load(request_or_site=request)
    form = EnquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not form.cleaned_data.get("website"):
            form.save()
        messages.success(request, "Thanks, we've got your message. We usually reply on WhatsApp within a working day.")
        return redirect("contact")
    return render(request, "core/contact.html", {"form": form, "site": site, "nav": "contact"})


def rooms(request):
    from .models import SPACES, Room
    site = SiteContent.load(request_or_site=request)
    rooms = Room.objects.filter(is_published=True).select_related("image").prefetch_related(
        "items__product__product_type__category", "items__variant", "items__product__cutout")
    products, data = {}, []
    for r in rooms:
        items = []
        for it in r.items.all():
            p = it.product
            if p.pk not in products:
                img = p.cutout.get_rendition("max-400x400|format-webp").url if p.cutout else ""
                products[p.pk] = {"name": p.name, "spec": p.short, "img": img, "url": p.get_absolute_url()}
            v = it.variant
            items.append({"p": p.pk, "role": it.role, "v": v.label if v else "", "price": (v.price or None) if v else None,
                          "qty": it.qty, "x": float(it.x), "y": float(it.y)})
        data.append({"id": r.slug, "name": r.title, "kind": r.get_space_display(), "group": r.group,
                     "img": r.image.get_rendition("fill-960x1200|format-webp").url, "tone": r.tone, "why": r.why,
                     "illus": r.is_illustrative, "items": items})
    return render(request, "projects/rooms.html", {"rooms_data": data, "products_data": products, "site": site, "nav": "rooms"})
