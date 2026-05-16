import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Follow, Profile
from apps.accounts.services.auth import AuthService
from apps.images.models import Collection, Image, ImageStatus, Like

User = get_user_model()

SEED_USERS = [
    {"username": "elsayed", "email": "elsayed@example.com", "password": "admin1234", "bio": "Building things.", "superuser": True},
    {"username": "sara_design", "email": "sara@example.com", "password": "pass1234", "bio": "UI designer & visual thinker."},
    {"username": "marco_photo", "email": "marco@example.com", "password": "pass1234", "bio": "Street photography."},
    {"username": "lena_art", "email": "lena@example.com", "password": "pass1234", "bio": "Digital artist."},
]

SEED_IMAGES = [
    {
        "title": "Golden Hour Architecture",
        "description": "Warm light washing over brutalist concrete forms.",
        "tags": ["architecture", "photography", "golden-hour"],
    },
    {
        "title": "Minimal Workspace Setup",
        "description": "Clean desk, clear mind.",
        "tags": ["workspace", "minimal", "design"],
    },
    {
        "title": "Abstract Color Study",
        "description": "Playing with complementary palettes.",
        "tags": ["abstract", "color", "art"],
    },
    {
        "title": "Night City Reflections",
        "description": "Rain-soaked streets after midnight.",
        "tags": ["photography", "night", "urban"],
    },
    {
        "title": "Swiss Typography",
        "description": "Helvetica and grid systems.",
        "tags": ["typography", "design", "swiss"],
    },
    {
        "title": "Coastal Geometry",
        "description": "Aerial view of wave patterns.",
        "tags": ["nature", "photography", "aerial"],
    },
    {
        "title": "Dark Mode UI Kit",
        "description": "Component library for modern apps.",
        "tags": ["ui", "design", "dark-mode"],
    },
    {
        "title": "Forest Light",
        "description": "Morning mist filtering through old growth.",
        "tags": ["nature", "photography", "forest"],
    },
]


class Command(BaseCommand):
    help = "Seed the database with realistic demo data"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear existing seed data first")

    @transaction.atomic
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
                self.stdout.write(f"  ↳ {user.username} already exists, skipping.")
            else:
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
        for i, data in enumerate(SEED_IMAGES):
            owner = users[i % len(users)]
            from shared.utils.slugify import unique_slug
            slug = unique_slug(data["title"], Image)
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
                },
            )
            if created:
                image.tags.add(*data["tags"])
                # Random likes from other users
                for user in random.sample(users, k=random.randint(0, len(users))):
                    Like.objects.get_or_create(user=user, image=image)
                self.stdout.write(f"  ↳ Created '{image.title}'")

        self.stdout.write(self.style.SUCCESS("\nSeed complete."))
        self.stdout.write("  Superuser → elsayed@example.com / admin1234")
        self.stdout.write(f"  Users: {', '.join('@' + u.username for u in users)}")
