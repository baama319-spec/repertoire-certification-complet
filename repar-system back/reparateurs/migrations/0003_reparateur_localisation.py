from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reparateurs", "0006_alter_reparateur_statut_verification"),
    ]

    operations = [
        migrations.AddField(
            model_name="reparateur",
            name="latitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="reparateur",
            name="longitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]