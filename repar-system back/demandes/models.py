from django.db import models
class DemandeMiseEnRelation(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        ACCEPTEE = "ACCEPTEE", "Acceptée"
        REFUSEE = "REFUSEE", "Refusée"
        ANNULEE = "ANNULEE", "Annulée"
    class Source(models.TextChoices):
        RECHERCHE = "RECHERCHE", "Recherche"
        RECOMMANDATION_IA = "RECOMMANDATION_IA", "Recommandation IA"
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="demandes")
    reparateur = models.ForeignKey("reparateurs.Reparateur", on_delete=models.SET_NULL, null=True, blank=True, related_name="demandes")
    localisation = models.ForeignKey("localisations.Localisation", on_delete=models.PROTECT, related_name="demandes")
    specialite = models.ForeignKey("specialites.Specialite", on_delete=models.SET_NULL, null=True, blank=True, related_name="demandes")
    description_probleme = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_reponse = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    source = models.CharField(max_length=25, choices=Source.choices, default=Source.RECHERCHE)
    class Meta: ordering = ("-date_creation",)
    def __str__(self): return f"Demande #{self.pk}"
class PieceJointe(models.Model):
    demande = models.ForeignKey(DemandeMiseEnRelation, on_delete=models.CASCADE, related_name="pieces_jointes")
    nom_fichier = models.CharField(max_length=255)
    fichier = models.FileField(upload_to="demandes/")
    type = models.CharField(max_length=100, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
