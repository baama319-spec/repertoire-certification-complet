from django.db import models
class Realisation(models.Model):
    reparateur = models.ForeignKey("reparateurs.Reparateur", on_delete=models.CASCADE, related_name="realisations")
    titre = models.CharField(max_length=180)
    description = models.TextField()
    photo = models.ImageField(upload_to="realisations/", blank=True, null=True)
    photo_avant = models.ImageField(upload_to="realisations/avant/", blank=True, null=True)
    photo_apres = models.ImageField(upload_to="realisations/apres/", blank=True, null=True)
    specialite = models.ForeignKey("specialites.Specialite", on_delete=models.SET_NULL, null=True, related_name="realisations")
    date_realisation = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ("-date_realisation",)
