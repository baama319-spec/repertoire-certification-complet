from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import DemandeMiseEnRelation, PieceJointe
class DemandeSerializer(ModelSerializer):
    client_detail = serializers.SerializerMethodField()
    reparateur_detail = serializers.SerializerMethodField()
    localisation_detail = serializers.SerializerMethodField()
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
    class Meta:
        model = DemandeMiseEnRelation
        fields = "__all__"
        read_only_fields = ("client", "date_creation", "date_reponse")
class PieceJointeSerializer(ModelSerializer):
    class Meta: model = PieceJointe; fields = "__all__"; read_only_fields = ("date_ajout",)
