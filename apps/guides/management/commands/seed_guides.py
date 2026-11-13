"""Starter guides so the Guides pages have something to show. Safe to run again: existing guides are left alone."""
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from wagtail.images.models import Image

from apps.catalogue.models import Product
from apps.guides.models import Guide

IMG = Path(settings.BASE_DIR) / "static" / "img" / "home"

GUIDES = [
    dict(slug="how-many-downlights-per-room", title="How many downlights do you need per room?", topic="buying", featured=True,
         summary="A simple size-to-quantity guide for living rooms, bedrooms, kitchens and shops, with spacing that avoids dark corners.",
         cover="coll-cob.webp", products=["Tulip", "Mini COB", "OPPLE"], published_on=date(2026, 11, 14),
         body="<p>Most people either under-light a room or fill the ceiling with dots. A good starting point is simple: decide how bright the room needs to be, then divide.</p>"
              "<h2>The quick rule</h2><p>For living areas, aim for roughly 100 lumens per square foot of floor, a little more for kitchens and shops. A typical 12W COB downlight gives about 1000 lumens.</p>"
              "<blockquote><p>Rule of thumb: one 12W downlight for every 10 square feet in living areas, spaced about one ceiling height apart.</p></blockquote>"
              "<h2>Quantities by room size</h2><ul><li>Bedroom, 12 × 12 ft: 6 to 8 downlights</li><li>Living room, 14 × 18 ft: 10 to 12</li><li>Kitchen, 10 × 12 ft: 6 to 8</li><li>Small shop, 12 × 20 ft: 12 to 16</li></ul>"
              "<h2>Spacing</h2><ul><li>Keep fittings about one ceiling height apart.</li><li>Stay about 2 ft from the walls.</li><li>Put them on a dimmer, or two circuits, so you can lower the light in the evening.</li></ul>"
              "<p>High ceilings and dark finishes need more light. Send us the dimensions and we will count it for you.</p>"
              "<p><em>Placeholder text: check the numbers and replace with your own advice.</em></p>"),
    dict(slug="warm-white-or-cool-white", title="Warm white or cool white: what to use in each room", topic="colour",
         summary="3000K, 4000K and 6500K explained, and why mixing them in one room looks wrong.",
         cover="hero.webp", products=["Tulip", "Linea"], published_on=date(2026, 11, 13),
         body="<p>The colour of white light is measured in Kelvin. Lower numbers are warmer and yellower, higher numbers are cooler and bluer.</p>"
              "<h2>3000K, warm white</h2><p>Cosy and flattering. Best for bedrooms, living rooms, dining areas and hotels.</p>"
              "<h2>4000K, neutral white</h2><p>Clean without feeling cold. A good choice for kitchens, offices and most shops.</p>"
              "<h2>6500K, cool white</h2><p>Very blue and harsh in homes. Use it only where you need maximum alertness, such as workshops and parking areas.</p>"
              "<blockquote><p>Pick one colour per room. Mixing 3000K and 6500K side by side makes a room look patchy.</p></blockquote>"
              "<p><em>Placeholder text: replace with your own advice.</em></p>"),
    dict(slug="laser-blade-vs-cob-downlight-vs-track-light", title="Laser blade vs COB downlight vs track light", topic="buying",
         summary="What each one does best, and when to combine them in the same space.",
         cover="coll-blade.webp", products=["Linea", "Rayzen Linear", "Decor Series"], published_on=date(2026, 11, 12),
         body="<p>These three cover most of what a home or shop needs. They do different jobs, so the right answer is often a mix.</p>"
              "<h2>COB downlights</h2><p>Round recessed lights that give even general light. The easy default for most rooms.</p>"
              "<h2>Laser blades</h2><p>Slim recessed lines of light. They suit corridors, reception areas and modern ceilings, and can be installed in rows.</p>"
              "<h2>Track lights</h2><p>Spotlights on a rail that you can re-aim. Best where displays or furniture change, like shops and galleries.</p>"
              "<p><em>Placeholder text: replace with your own advice.</em></p>"),
    dict(slug="lighting-a-shop", title="Lighting a shop so products look better", topic="shops",
         summary="Track light angles, colour rendering and glare: the basics that make a display look expensive.",
         cover="coll-track.webp", products=["Decor Series", "Track"], published_on=date(2026, 11, 11),
         body="<p>Good shop lighting is mostly about directing light at the product, not at the floor.</p>"
              "<h2>Light the display, not the aisle</h2><p>Aim track spots at about 30 degrees from vertical so light lands on the product without glare in customers' eyes.</p>"
              "<h2>Choose good colour rendering</h2><p>Look for CRI 90 or more where colour matters, such as clothing and furniture.</p>"
              "<p><em>Placeholder text: replace with your own advice.</em></p>"),
]


def image(name):
    title = f"Guide placeholder · {name}"
    found = Image.objects.filter(title=title).first()
    if found:
        return found
    path = IMG / name
    with open(path, "rb") as fh:
        img = Image(title=title)
        img.file.save(name, ImageFile(fh), save=False)
    img.save()
    return img


class Command(BaseCommand):
    help = "Create starter guides if they do not exist."

    def handle(self, *args, **opts):
        made = 0
        for d in GUIDES:
            if Guide.objects.filter(slug=d["slug"]).exists():
                continue
            g = Guide(slug=d["slug"], title=d["title"], topic=d["topic"], summary=d["summary"], body=d["body"],
                      featured=d.get("featured", False), published_on=d["published_on"], cover=image(d["cover"]))
            g.save()
            names = d["products"]
            prods = [p for p in Product.objects.all() if any(n.lower() in p.name.lower() for n in names)]
            g.products = prods
            g.save()
            made += 1
        self.stdout.write(f"Guides: {made} created, {Guide.objects.count()} total.")
