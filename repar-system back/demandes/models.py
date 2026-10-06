from django.db import models
class DemandeMiseEnRelation(models.Model):
    class ModeIntervention(models.TextChoices):
        DOMICILE = "DOMICILE", "À domicile"
        ATELIER = "ATELIER", "À l’atelier du réparateur"

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
    appareil = models.CharField(max_length=120, blank=True, default="")
    description_probleme = models.TextField()
    mode_intervention = models.CharField(max_length=12, choices=ModeIntervention.choices, default=ModeIntervention.DOMICILE)
    adresse_intervention = models.CharField(max_length=255, blank=True, default="")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    diagnostic_ia = models.JSONField(default=dict, blank=True)
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
