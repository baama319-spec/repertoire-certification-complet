from django.db import models
class Localisation(models.Model):
    nom = models.CharField(max_length=150, blank=True)
    adresse = models.CharField(max_length=255)
    quartier = models.CharField(max_length=120, blank=True)
    ville = models.CharField(max_length=120)
    actif = models.BooleanField(default=True)
    def __str__(self): return f"{self.ville} — {self.adresse}"
