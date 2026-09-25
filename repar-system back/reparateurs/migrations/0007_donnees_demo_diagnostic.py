from django.db import migrations


SPECIALITES = [
    ("Réparation de tablettes", "Écrans, batteries et connectique des tablettes."),
    ("Réparation de téléviseurs", "Pannes d'image, de son et d'alimentation des téléviseurs."),
]

ZONES = [
    ("Dakar Plateau", "Dakar", "Dakar Plateau"),
    ("Mermoz", "Dakar", "Mermoz"),
    ("Liberté 6", "Dakar", "Liberté 6"),
]


def ajouter_donnees_demo(apps, schema_editor):
    Reparateur = apps.get_model("reparateurs", "Reparateur")
    Specialite = apps.get_model("specialites", "Specialite")
    Localisation = apps.get_model("localisations", "Localisation")

    specialites = {
        nom: Specialite.objects.get_or_create(
            nom=nom,
            defaults={"description": description, "actif": True},
        )[0]
        for nom, description in SPECIALITES
    }
    specialites.update({item.nom: item for item in Specialite.objects.filter(actif=True)})

    zones = []
    for nom, ville, quartier in ZONES:
        zone, _ = Localisation.objects.get_or_create(
            ville=ville,
            quartier=quartier,
            defaults={"nom": nom, "adresse": nom, "actif": True},
        )
        zones.append(zone)

    profils = list(
        Reparateur.objects.filter(profil_verifie=True)
        .order_by("id")[:3]
    )
    associations = [
        ("Réparation de smartphones", "Réparation de tablettes"),
        ("Informatique et ordinateurs", "Réparation de téléviseurs"),
        ("Électronique grand public", "Réparation de téléviseurs"),
    ]
    for index, profil in enumerate(profils):
        profil.specialites.add(*[
            specialites[nom]
            for nom in associations[index]
            if nom in specialites
        ])
        profil.zones_intervention.add(zones[index % len(zones)])


def supprimer_donnees_demo(apps, schema_editor):
    Specialite = apps.get_model("specialites", "Specialite")
    Specialite.objects.filter(
        nom__in=("Réparation de tablettes", "Réparation de téléviseurs")
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("reparateurs", "0003_reparateur_localisation"),
        ("specialites", "0002_donnees_diagnostic"),
        ("localisations", "0003_donnees_diagnostic"),
    ]
    operations = [migrations.RunPython(ajouter_donnees_demo, supprimer_donnees_demo)]
