from django.db import migrations


ZONES_DIAGNOSTIC = [
    ("Dakar Plateau", "Dakar", "Dakar Plateau"),
    ("Mermoz", "Dakar", "Mermoz"),
    ("Liberté 6", "Dakar", "Liberté 6"),
    ("Saint-Louis Centre", "Saint-Louis", "Saint-Louis Centre"),
    ("Diourbel Centre", "Diourbel", "Diourbel Centre"),
]


def ajouter_zones(apps, schema_editor):
    Localisation = apps.get_model("localisations", "Localisation")
    for nom, ville, quartier in ZONES_DIAGNOSTIC:
        Localisation.objects.get_or_create(
            ville=ville,
            quartier=quartier,
            defaults={"nom": nom, "adresse": nom, "actif": True},
        )


def supprimer_zones(apps, schema_editor):
    Localisation = apps.get_model("localisations", "Localisation")
    for _, ville, quartier in ZONES_DIAGNOSTIC:
        Localisation.objects.filter(ville=ville, quartier=quartier).delete()


class Migration(migrations.Migration):
    dependencies = [("localisations", "0002_supprimer_coordonnees_zone")]
    operations = [migrations.RunPython(ajouter_zones, supprimer_zones)]
