from django.db import models
class Specialite(models.Model):
    nom = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to="categories/", blank=True, null=True)
    actif = models.BooleanField(default=True)
    def __str__(self): return self.nom
