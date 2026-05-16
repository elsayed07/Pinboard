import random

import logging

import httpx
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Follow, Profile
from apps.accounts.services.auth import AuthService
from apps.images.models import Image, ImageStatus, Like

User = get_user_model()

SEED_USERS = [
    {"username": "elsayed", "email": "elsayed@example.com", "password": "admin1234", "bio": "Building things.", "superuser": True},
    {"username": "sara_design", "email": "sara@example.com", "password": "pass1234", "bio": "UI designer & visual thinker."},
    {"username": "marco_photo", "email": "marco@example.com", "password": "pass1234", "bio": "Street photography."},
    {"username": "lena_art", "email": "lena@example.com", "password": "pass1234", "bio": "Digital artist."},
]

# Picsum seed values give deterministic, visually distinct images
SEED_IMAGES = [
    {"title": "Golden Hour Architecture", "description": "Warm light washing over brutalist concrete forms.", "tags": ["architecture", "photography", "golden-hour"], "picsum": 10},
    {"title": "Minimal Workspace Setup", "description": "Clean desk, clear mind.", "tags": ["workspace", "minimal", "design"], "picsum": 20},
    {"title": "Abstract Color Study", "description": "Playing with complementary palettes.", "tags": ["abstract", "color", "art"], "picsum": 30},
    {"title": "Night City Reflections", "description": "Rain-soaked streets after midnight.", "tags": ["photography", "night", "urban"], "picsum": 40},
    {"title": "Swiss Typography", "description": "Helvetica and grid systems.", "tags": ["typography", "design", "swiss"], "picsum": 50},
    {"title": "Coastal Geometry", "description": "Aerial view of wave patterns.", "tags": ["nature", "photography", "aerial"], "picsum": 60},
    {"title": "Dark Mode UI Kit", "description": "Component library for modern apps.", "tags": ["ui", "design", "dark-mode"], "picsum": 70},
    {"title": "Forest Light", "description": "Morning mist filtering through old growth.", "tags": ["nature", "photography", "forest"], "picsum": 80},
]


def _fetch_image(picsum_id: int, width: int, height: int) -> bytes:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    url = f"https://picsum.photos/id/{picsum_id}/{width}/{height}"
    resp = httpx.get(url, follow_redirects=True, timeout=20)
    resp.raise_for_status()
    return resp.content


class Command(BaseCommand):
    help = "Seed the database with realistic demo data"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear existing seed data first")
        parser.add_argument("--no-images", action="store_true", help="Skip downloading images from Picsum")

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            Image.all_objects.all().delete()
            Follow.objects.all().delete()
            User.objects.filter(email__endswith="@example.com").delete()

        self.stdout.write("Creating users...")
        users = []
        for data in SEED_USERS:
            if User.objects.filter(email=data["email"]).exists():
                user = User.objects.get(email=data["email"])
                self.stdout.write(f"  ↳ @{user.username} already exists, skipping.")
            else:
                with transaction.atomic():
                    if data.get("superuser"):
                        user = User.objects.create_superuser(
                            email=data["email"],
                            username=data["username"],
                            password=data["password"],
                        )
                    else:
                        user = AuthService.register(
                            email=data["email"],
                            username=data["username"],
                            password=data["password"],
                        )
                    Profile.objects.filter(user=user).update(bio=data.get("bio", ""))
                self.stdout.write(f"  ↳ Created @{user.username}")
            users.append(user)

        self.stdout.write("Creating follow relationships...")
        for i, follower in enumerate(users):
            for j, following in enumerate(users):
                if i != j and random.random() > 0.3:
                    Follow.objects.get_or_create(follower=follower, following=following)

        self.stdout.write("Creating images...")
        skip_download = options["no_images"]

        for i, data in enumerate(SEED_IMAGES):
            owner = users[i % len(users)]
            from shared.utils.slugify import unique_slug
            slug = unique_slug(data["title"], Image)

            with transaction.atomic():
                image, created = Image.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "owner": owner,
                        "title": data["title"],
                        "description": data["description"],
                        "status": ImageStatus.READY,
                        "privacy": "public",
                        "like_count": random.randint(0, 120),
                        "view_count": random.randint(50, 2000),
                        "width": 800,
                        "height": 600,
                    },
                )

            if created:
                image.tags.add(*data["tags"])

                if not skip_download:
                    try:
                        self.stdout.write(f"  ↳ Downloading image for '{data['title']}'...")
                        full_bytes = _fetch_image(data["picsum"], 800, 600)
                        thumb_bytes = _fetch_image(data["picsum"], 400, 300)
                        fname = f"{image.slug}.jpg"
                        image.image.save(fname, ContentFile(full_bytes), save=False)
                        image.thumbnail.save(f"thumb_{fname}", ContentFile(thumb_bytes), save=False)
                        image.save(update_fields=["image", "thumbnail"])
                        self.stdout.write(f"     ✓ saved")
                    except Exception as exc:
                        self.stdout.write(self.style.WARNING(f"     ⚠ download failed: {exc}"))

                for user in random.sample(users, k=random.randint(0, len(users))):
                    Like.objects.get_or_create(user=user, image=image)

                self.stdout.write(f"  ↳ Created '{image.title}'")

        self.stdout.write(self.style.SUCCESS("\nSeed complete."))
        self.stdout.write("  Superuser → elsayed@example.com / admin1234")
        self.stdout.write(f"  Users: {', '.join('@' + u.username for u in users)}")
