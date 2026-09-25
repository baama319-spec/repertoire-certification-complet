from django.conf import settings
from django.db import models
class Notification(models.Model):
    class Type(models.TextChoices):
        NOUVELLE_DEMANDE = "NOUVELLE_DEMANDE", "Nouvelle demande"
        DEMANDE_ACCEPTEE = "DEMANDE_ACCEPTEE", "Demande acceptée"
        DEMANDE_REFUSEE = "DEMANDE_REFUSEE", "Demande refusée"
        NOUVEL_AVIS = "NOUVEL_AVIS", "Nouvel avis"
        SYSTEME = "SYSTEME", "Système"
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    titre = models.CharField(max_length=180)
    message = models.TextField()
    type = models.CharField(max_length=25, choices=Type.choices)
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ("-date_creation",)
