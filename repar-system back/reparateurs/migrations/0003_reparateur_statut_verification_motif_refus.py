from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("reparateurs", "0002_initial")]

    operations = [
        migrations.AddField(model_name="reparateur", name="statut_verification", field=models.CharField(choices=[("EN_ATTENTE", "En attente"), ("REFUSEE", "Refusée"), ("VERIFIEE", "Vérifiée")], default="EN_ATTENTE", max_length=20)),
        migrations.AddField(model_name="reparateur", name="motif_refus", field=models.TextField(blank=True)),
    ]
