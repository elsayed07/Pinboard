from django.contrib.postgres.search import SearchVector
from django.core.management.base import BaseCommand

from apps.images.models import Image, ImageStatus


class Command(BaseCommand):
    help = "Backfill search_vector for all ready images that have not been indexed yet."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Re-index all ready images, not just those with a null search_vector.",
        )

    def handle(self, *args, **options):
        qs = Image.objects.filter(status=ImageStatus.READY)
        if not options["all"]:
            qs = qs.filter(search_vector__isnull=True)

        total = qs.count()
        if not total:
            self.stdout.write("Nothing to index.")
            return

        qs.update(
            search_vector=(
                SearchVector("title", weight="A")
                + SearchVector("description", weight="B")
            )
        )
        self.stdout.write(self.style.SUCCESS(f"Indexed {total} image(s)."))
