from django.db import migrations


def migrer(apps, schema_editor):
    Reparateur = apps.get_model("reparateurs", "Reparateur")
    Reparateur.objects.filter(statut_verification="VERIFIEE").update(statut_verification="VALIDEE")


class Migration(migrations.Migration):
    dependencies = [("reparateurs", "0004_synchroniser_profils_verifies")]
    operations = [migrations.RunPython(migrer, migrations.RunPython.noop)]
