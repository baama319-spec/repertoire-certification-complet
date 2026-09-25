from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("reparateurs", "0005_remplacer_verifiee_par_validee")]
    operations = [
        migrations.AlterField(
            model_name="reparateur",
            name="statut_verification",
            field=models.CharField(choices=[("EN_ATTENTE", "En attente"), ("REFUSEE", "Refusée"), ("VALIDEE", "Validée")], default="EN_ATTENTE", max_length=20),
        ),
    ]
