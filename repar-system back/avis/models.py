from django.db import models
class Avis(models.Model):
    demande = models.OneToOneField("demandes.DemandeMiseEnRelation", on_delete=models.CASCADE, related_name="avis")
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="avis")
    reparateur = models.ForeignKey("reparateurs.Reparateur", on_delete=models.CASCADE, related_name="avis")
    note = models.PositiveSmallIntegerField()
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
