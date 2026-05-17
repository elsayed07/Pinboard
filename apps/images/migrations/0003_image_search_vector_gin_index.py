from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0002_uuid_tagged_item"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="image",
            index=GinIndex(fields=["search_vector"], name="image_search_vector_gin"),
        ),
    ]
