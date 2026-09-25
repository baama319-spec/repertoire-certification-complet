from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("specialites", "0002_specialite_actif"),
    ]

    operations = [
        migrations.AddField(
            model_name="specialite",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="categories/"),
        ),
    ]
