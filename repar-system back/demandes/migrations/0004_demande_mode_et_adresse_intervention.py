from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("demandes", "0003_demande_appareil"),
    ]

    operations = [
        migrations.AddField(
            model_name="demandemiseenrelation",
            name="mode_intervention",
            field=models.CharField(
                choices=[("DOMICILE", "À domicile"), ("ATELIER", "À l’atelier du réparateur")],
                default="DOMICILE",
                max_length=12,
            ),
        ),
        migrations.AddField(
            model_name="demandemiseenrelation",
            name="adresse_intervention",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
