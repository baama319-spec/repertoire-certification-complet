from django.db import migrations


SPECIALITES_DIAGNOSTIC = {
    "Réparation de smartphones": "Téléphones, écrans, batteries et problèmes de charge.",
    "Informatique et ordinateurs": "Ordinateurs portables, systèmes et surchauffe.",
    "Électronique grand public": "Téléviseurs, tablettes et équipements électroniques.",
}


def ajouter_specialites(apps, schema_editor):
    Specialite = apps.get_model("specialites", "Specialite")
    for nom, description in SPECIALITES_DIAGNOSTIC.items():
        Specialite.objects.get_or_create(nom=nom, defaults={"description": description, "actif": True})


def supprimer_specialites(apps, schema_editor):
    Specialite = apps.get_model("specialites", "Specialite")
    Specialite.objects.filter(nom__in=SPECIALITES_DIAGNOSTIC).delete()


class Migration(migrations.Migration):
    dependencies = [("specialites", "0003_specialite_photo")]
    operations = [migrations.RunPython(ajouter_specialites, supprimer_specialites)]
