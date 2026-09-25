from django.conf import settings
from django.db import models
class Reparateur(models.Model):
    class StatutVerification(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        REFUSEE = "REFUSEE", "Refusée"
        VALIDEE = "VALIDEE", "Validée"

    utilisateur = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profil_reparateur")
    description = models.TextField(blank=True)
    annee_experience = models.PositiveSmallIntegerField(default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    profil_verifie = models.BooleanField(default=False)
    statut_verification = models.CharField(max_length=20, choices=StatutVerification.choices, default=StatutVerification.EN_ATTENTE)
    motif_refus = models.TextField(blank=True)
    date_verification = models.DateTimeField(null=True, blank=True)
    specialites = models.ManyToManyField("specialites.Specialite", related_name="reparateurs", blank=True)
    zones_intervention = models.ManyToManyField("localisations.Localisation", related_name="reparateurs_intervenants", blank=True)
    def __str__(self): return str(self.utilisateur)
