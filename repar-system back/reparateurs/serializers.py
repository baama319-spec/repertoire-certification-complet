from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from utilisateurs.serializers import UtilisateurSerializer
from .models import Reparateur


class CoordonneesField(serializers.DecimalField):
    def to_internal_value(self, data):
        try:
            data = Decimal(str(data)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        except (TypeError, ValueError, ArithmeticError):
            pass
        return super().to_internal_value(data)


class ReparateurSerializer(ModelSerializer):
    # Les pages publiques, listes et écrans d'administration reçoivent la même
    # photo que celle affichée dans l'espace professionnel.
    utilisateur_detail = UtilisateurSerializer(source="utilisateur", read_only=True)
    specialites_detail = serializers.SerializerMethodField()
    zones_intervention_detail = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    latitude = CoordonneesField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = CoordonneesField(max_digits=9, decimal_places=6, required=False, allow_null=True)

    def get_specialites_detail(self, reparateur):
        return [{"id": item.id, "nom": item.nom} for item in reparateur.specialites.all()]

    def get_zones_intervention_detail(self, reparateur):
        return [{"id": item.id, "nom": item.nom, "ville": item.ville, "quartier": item.quartier} for item in reparateur.zones_intervention.all()]

    def get_distance_km(self, reparateur):
        distance = self.context.get("distance_km")
        return round(distance, 1) if distance is not None else None
    class Meta:
        model = Reparateur
        fields = "__all__"
        read_only_fields = ("utilisateur", "profil_verifie", "statut_verification", "motif_refus", "date_verification")
