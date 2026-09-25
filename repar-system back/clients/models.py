from django.conf import settings
from django.db import models
class Client(models.Model):
    utilisateur = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profil_client")
    zone_residence = models.ForeignKey("localisations.Localisation", on_delete=models.SET_NULL, null=True, blank=True, related_name="clients_residents")
    adresse_principale = models.CharField(max_length=255, blank=True)
    def __str__(self): return str(self.utilisateur)
