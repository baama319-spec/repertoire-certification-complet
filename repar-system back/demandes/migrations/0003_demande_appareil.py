from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("demandes", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="demandemiseenrelation",
            name="appareil",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
    ]
