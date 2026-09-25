from django.db import migrations


ASSOCIATIONS = [
    ("Réparation de tablettes", "Réparation de téléviseurs"),
    ("Réparation de smartphones", "Électronique grand public"),
    ("Informatique et ordinateurs", "Climatisation"),
]


def completer_reparateurs_demo(apps, schema_editor):
    Reparateur = apps.get_model("reparateurs", "Reparateur")
    Specialite = apps.get_model("specialites", "Specialite")
    Localisation = apps.get_model("localisations", "Localisation")

    noms_specialites = {item.nom: item for item in Specialite.objects.filter(actif=True)}
    zones = list(Localisation.objects.filter(ville="Dakar", actif=True).order_by("id"))
    profils = list(Reparateur.objects.order_by("id")[3:6])

    for index, profil in enumerate(profils):
        profil.profil_verifie = True
        profil.statut_verification = "VALIDEE"
        profil.save(update_fields=("profil_verifie", "statut_verification"))
        profil.specialites.add(*[
            noms_specialites[nom]
            for nom in ASSOCIATIONS[index]
            if nom in noms_specialites
        ])
        if zones:
            profil.zones_intervention.add(zones[index % len(zones)])


def annuler(apps, schema_editor):
    Reparateur = apps.get_model("reparateurs", "Reparateur")
    Reparateur.objects.filter(id__in=(4, 5, 6)).update(profil_verifie=False, statut_verification="EN_ATTENTE")


class Migration(migrations.Migration):
    dependencies = [("reparateurs", "0007_donnees_demo_diagnostic")]
    operations = [migrations.RunPython(completer_reparateurs_demo, annuler)]
