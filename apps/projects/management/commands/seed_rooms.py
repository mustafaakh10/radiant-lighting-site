"""Dummy rooms for the Shop the Room page. Safe to run again: existing rooms are left alone."""
from pathlib import Path

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from wagtail.images.models import Image

from apps.catalogue.models import Product, ProductVariant
from apps.projects.models import Room, RoomItem

IMG = Path(settings.BASE_DIR) / "static" / "img" / "rooms"
W = "<b>Why it works:</b> "
ROOMS = [
    dict(slug="warm-living-room", title="The Warm Living Room", space="living", img="living.webp", tone=3000,
         why="Spots set about 70cm from the wall wash it in soft arcs of light, so the room glows without one bright light in the middle of the ceiling.",
         items=[("Tulip", "12W", "Wall-washing spots", 6, 49, 12), ("OPPLE", None, "General light, glare-free", 4, 11, 8),
                ("Mini COB", "1-inch", "Accent over the flowers", 2, 80, 15)]),
    dict(slug="reception-lobby", title="The Reception Lobby", space="office", img="lobby.webp", tone=3000,
         why="Recessed blades light the walkway without glare, wall spots pick out the timber slats, and a line of strip under the counter makes it look like it floats.",
         items=[("Linea", "3 heads", "Ceiling, walkway light", 6, 47, 4), ("Tulip", "12W", "Spots on the slatted wall", 4, 72, 21),
                ("Rayzen Linear", "20W", "Long lines of light", 2, 79, 34), ("COB Strip", "24V", "Glow under the counter", 1, 71, 79)]),
    dict(slug="quiet-hotel-corner", title="The Quiet Hotel Corner", space="hotel", img="hotel.webp", tone=3000,
         why="Hidden strip in the ceiling cove and behind the bench lights the slatted wall from above and below, while small multi-head blades put soft pools of light on the plain walls.",
         items=[("Linea", "3 heads", "Multi-head wall wash", 2, 81, 12), ("Rayzen Square", None, "Square grille, second wall", 1, 61, 20),
                ("COB Strip", "24V", "Ceiling cove and bench glow", 2, 27, 8)]),
    dict(slug="gallery-lounge", title="The Gallery Lounge", space="living", img="lounge.webp", tone=4000,
         why="Three spots on one rail, aimed down the wall, turn a plain wall into a feature. Re-aim them any time you hang new art.",
         items=[("Decor Series", "10W", "Spots aimed at the wall", 3, 69, 35), ("Aluminium Track", "1 metre", "Rail to mount them on", 2, 40, 31)]),
]


class Command(BaseCommand):
    help = "Create dummy rooms for the Shop the Room page (skips any that exist)."

    def handle(self, *args, **opts):
        made = 0
        for i, d in enumerate(ROOMS):
            if Room.objects.filter(slug=d["slug"]).exists():
                continue
            title = f"Room placeholder · {d['img']}"
            img = Image.objects.filter(title=title).first()
            if not img:
                with open(IMG / d["img"], "rb") as fh:
                    img = Image(title=title, file=ImageFile(fh, name=f"room-{d['img']}"))
                    img.save()
            room = Room(slug=d["slug"], title=d["title"], space=d["space"], image=img, tone=d["tone"], why=d["why"], sort_order=i)
            room.save()
            for n, (name, label, role, qty, x, y) in enumerate(d["items"]):
                p = Product.objects.filter(name__istartswith=name).first()
                if not p:
                    continue
                v = ProductVariant.objects.filter(product=p, label=label).first() if label else None
                RoomItem.objects.create(room=room, product=p, variant=v, role=role, qty=qty, x=x, y=y, sort_order=n)
            made += 1
        self.stdout.write(self.style.SUCCESS(f"Rooms: {made} created, {Room.objects.count()} total."))
