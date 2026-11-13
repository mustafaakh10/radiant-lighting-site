"""Dummy projects so the Projects pages have something to show. Safe to run again: existing projects are left alone."""
from pathlib import Path

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from wagtail.images.models import Image

from apps.catalogue.models import Product
from apps.projects.models import Project, ProjectPhoto

IMG = Path(settings.BASE_DIR) / "static" / "img" / "home"

PROJECTS = [
    dict(slug="crystal-arcade-offices", title="Crystal Arcade offices", kind="office", city="Multan", year=2025,
         summary="Reception, open office and meeting rooms lit with laser blades and COB downlights.",
         body="A full fit-out for a three-floor office in Crystal Arcade. The brief was bright, even light for desk work without glare on screens.\n\n"
              "We used recessed laser blades along the corridors and reception, and anti-glare COB downlights over the desks, all at 4000K.\n\n"
              "Placeholder text: replace with the real story, sizes and timeline.",
         cover="hero2.webp", photos=["hero2.webp", "coll-blade.webp", "coll-cob.webp"], products=["Linea", "Rayzen Linear", "OPPLE"]),
    dict(slug="dha-residence", title="Private residence, DHA", kind="home", city="Multan", year=2025,
         summary="Warm 3000K downlights and accent spots through a family home.",
         body="A new-build family home with a calm, warm feel. Living and dining areas use dimmable COB spots, with miniature spots picking out the art.\n\n"
              "Placeholder text: replace with the real story.",
         cover="hero.webp", photos=["hero.webp", "work-3.webp", "coll-cob.webp"], products=["Tulip", "Mini COB", "OPPLE"]),
    dict(slug="bosan-road-boutique", title="Boutique on Bosan Road", kind="retail", city="Multan", year=2024,
         summary="Track spotlights that move with the displays.",
         body="A clothing boutique that changes its displays every season. Track lighting lets the owner re-aim every spot in minutes.\n\n"
              "Placeholder text: replace with the real story.",
         cover="coll-track.webp", photos=["coll-track.webp", "coll-blade.webp"], products=["Decor Series", "Track"]),
    dict(slug="gulberg-commercial-complex", title="Commercial complex, Gulberg", kind="office", city="Lahore", year=2024,
         summary="Lobby, corridors and shopfronts across a four-storey complex.",
         body="Common areas and shopfronts for a mixed-use building, specified and supplied as one package.\n\n"
              "Placeholder text: replace with the real story.",
         cover="showroom.webp", photos=["showroom.webp", "hero2.webp"], products=["Rayzen Square", "Linea"]),
]


def image(name):
    title = f"Project placeholder · {name}"
    found = Image.objects.filter(title=title).first()
    if found:
        return found
    with open(IMG / name, "rb") as fh:
        img = Image(title=title, file=ImageFile(fh, name=f"project-{name}"))
        img.save()
    return img


class Command(BaseCommand):
    help = "Create dummy projects for the Projects pages (skips any that exist)."

    def handle(self, *args, **opts):
        made = 0
        for i, d in enumerate(PROJECTS):
            if Project.objects.filter(slug=d["slug"]).exists():
                continue
            p = Project(slug=d["slug"], title=d["title"], kind=d["kind"], city=d["city"], year=d["year"],
                        summary=d["summary"], body=d["body"], cover=image(d["cover"]), sort_order=i)
            p.save()
            for n, ph in enumerate(d["photos"]):
                ProjectPhoto.objects.create(project=p, image=image(ph), sort_order=n)
            prods = []
            for name in d["products"]:
                prods += list(Product.objects.filter(name__icontains=name)[:1])
            p.products.set(prods)
            p.save()
            made += 1
        self.stdout.write(self.style.SUCCESS(f"Projects: {made} created, {Project.objects.count()} total."))
