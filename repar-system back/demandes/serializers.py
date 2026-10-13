from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from localisations.models import Localisation
from specialites.models import Specialite
from reparateurs.models import Reparateur
from .models import DemandeMiseEnRelation, PieceJointe
class DemandeSerializer(ModelSerializer):
    localisation = serializers.PrimaryKeyRelatedField(queryset=Localisation.objects.filter(actif=True))
    specialite = serializers.PrimaryKeyRelatedField(queryset=Specialite.objects.filter(actif=True), required=False, allow_null=True)
    reparateur = serializers.PrimaryKeyRelatedField(
        queryset=Reparateur.objects.filter(
            statut_verification=Reparateur.StatutVerification.VALIDEE,
            utilisateur__actif=True,
        ),
        required=False,
        allow_null=True,
    )
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    client_detail = serializers.SerializerMethodField()
    reparateur_detail = serializers.SerializerMethodField()
    localisation_detail = serializers.SerializerMethodField()
    specialite_detail = serializers.SerializerMethodField()
    pieces_jointes = serializers.SerializerMethodField()
    def get_client_detail(self, obj):
        u = obj.client.utilisateur
        return {"id": obj.client_id, "nom": f"{u.prenom} {u.nom}", "telephone": u.telephone, "photo_profil": u.photo_profil.url if u.photo_profil else None}
    def get_reparateur_detail(self, obj):
        if not obj.reparateur_id: return None
        u = obj.reparateur.utilisateur
        return {"id": obj.reparateur_id, "nom": f"{u.prenom} {u.nom}", "photo_profil": u.photo_profil.url if u.photo_profil else None}
    def get_localisation_detail(self, obj):
        z = obj.localisation
        return {"id": z.id, "nom": z.nom, "ville": z.ville, "quartier": z.quartier, "adresse": z.adresse}
    def get_specialite_detail(self, obj):
        if not obj.specialite_id: return None
        return {"id": obj.specialite_id, "nom": obj.specialite.nom}
    def get_pieces_jointes(self, obj):
        request = self.context.get("request")
        pieces = []
        for piece in obj.pieces_jointes.all():
            url = piece.fichier.url if piece.fichier else None
            if url and request:
                url = request.build_absolute_uri(url)
            pieces.append({
                "id": piece.pk,
                "nom_fichier": piece.nom_fichier,
                "fichier": url,
                "type": piece.type,
            })
        return pieces
    def validate_description_probleme(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Décrivez le problème en 10 caractères minimum.")
        return value
    class Meta:
        model = DemandeMiseEnRelation
        fields = "__all__"
        read_only_fields = ("client", "date_creation", "date_reponse", "statut")
class PieceJointeSerializer(ModelSerializer):
    class Meta: model = PieceJointe; fields = "__all__"; read_only_fields = ("date_ajout",)
