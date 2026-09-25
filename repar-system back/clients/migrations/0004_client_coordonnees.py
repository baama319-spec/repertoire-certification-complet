import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("clients", "0003_remove_client_localisation_defaut"), ("localisations", "0002_localisation_actif")]

    operations = [
        migrations.AddField(model_name="client", name="adresse_principale", field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name="client", name="zone_residence", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="clients_residents", to="localisations.localisation")),
    ]
