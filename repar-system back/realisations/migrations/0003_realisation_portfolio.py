from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("realisations", "0002_initial"),
        ("specialites", "0002_specialite_actif"),
    ]

    operations = [
        migrations.AddField(model_name="realisation", name="photo_apres", field=models.ImageField(blank=True, null=True, upload_to="realisations/apres/")),
        migrations.AddField(model_name="realisation", name="photo_avant", field=models.ImageField(blank=True, null=True, upload_to="realisations/avant/")),
        migrations.AddField(model_name="realisation", name="specialite", field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="realisations", to="specialites.specialite")),
        migrations.AlterField(model_name="realisation", name="date_realisation", field=models.DateTimeField(auto_now_add=True)),
    ]
