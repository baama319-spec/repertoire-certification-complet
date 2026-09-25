from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("localisations", "0002_localisation_actif"),
    ]

    operations = [
        migrations.RemoveField(model_name="localisation", name="latitude"),
        migrations.RemoveField(model_name="localisation", name="longitude"),
    ]