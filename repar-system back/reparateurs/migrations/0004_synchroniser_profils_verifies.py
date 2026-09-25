from django.db import migrations


def synchroniser(apps, schema_editor):
    Reparateur = apps.get_model("reparateurs", "Reparateur")
    Reparateur.objects.filter(profil_verifie=True).update(statut_verification="VALIDEE")


class Migration(migrations.Migration):
    dependencies = [("reparateurs", "0003_reparateur_statut_verification_motif_refus")]
    operations = [migrations.RunPython(synchroniser, migrations.RunPython.noop)]
