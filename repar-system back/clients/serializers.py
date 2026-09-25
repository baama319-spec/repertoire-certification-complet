from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from utilisateurs.serializers import UtilisateurSerializer
from .models import Client
class ClientSerializer(ModelSerializer):
    # Rend l'avatar et les informations de compte disponibles aux interfaces
    # qui présentent un client (admin, demandes et avis).
    utilisateur_detail = UtilisateurSerializer(source="utilisateur", read_only=True)
    zone_residence_detail = serializers.SerializerMethodField()
    def get_zone_residence_detail(self, client):
        zone = client.zone_residence
        return None if not zone else {"id": zone.id, "nom": zone.nom, "ville": zone.ville, "quartier": zone.quartier}
    class Meta: model = Client; fields = "__all__"
