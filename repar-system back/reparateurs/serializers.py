from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from utilisateurs.serializers import UtilisateurSerializer
from .models import Reparateur, ReparateurDocument


class CoordonneesField(serializers.DecimalField):
    def to_internal_value(self, data):
        try:
            data = Decimal(str(data)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        except (TypeError, ValueError, ArithmeticError):
            pass
        return super().to_internal_value(data)


class ReparateurDocumentSerializer(ModelSerializer):
    class Meta:
        model = ReparateurDocument
        fields = ("id", "type_document", "document", "date_ajout")
        read_only_fields = ("id", "date_ajout")

    def get_document(self, obj):
        return obj.document.url if obj.document else None


class ReparateurSerializer(ModelSerializer):
    utilisateur_detail = UtilisateurSerializer(source="utilisateur", read_only=True)
    specialites_detail = serializers.SerializerMethodField()
    zones_intervention_detail = serializers.SerializerMethodField()
    documents_detail = serializers.SerializerMethodField()
    photo_carte_identite = serializers.SerializerMethodField(read_only=True)
    photo_carte_identite_upload = serializers.ImageField(write_only=True, source="photo_carte_identite", required=False)
    distance_km = serializers.SerializerMethodField()
    note_moyenne = serializers.FloatField(read_only=True, allow_null=True)
    nombre_avis = serializers.IntegerField(read_only=True)
    latitude = CoordonneesField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = CoordonneesField(max_digits=9, decimal_places=6, required=False, allow_null=True)

    def get_specialites_detail(self, reparateur):
        return [{"id": item.id, "nom": item.nom} for item in reparateur.specialites.all()]

    def get_zones_intervention_detail(self, reparateur):
        return [{"id": item.id, "nom": item.nom, "ville": item.ville, "quartier": item.quartier} for item in reparateur.zones_intervention.all()]

    def get_documents_detail(self, reparateur):
        return [{
            "id": document.id,
            "type_document": document.type_document,
            "document": document.document.url if document.document else None,
            "nom_fichier": document.document.name.split("/")[-1] if document.document else None,
        } for document in reparateur.documents.all()]

    def get_photo_carte_identite(self, reparateur):
        if not reparateur.photo_carte_identite:
            return None
        url = reparateur.photo_carte_identite.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_distance_km(self, reparateur):
        distance = self.context.get("distance_km")
        return round(distance, 1) if distance is not None else None

    class Meta:
        model = Reparateur
        fields = (
            "id", "utilisateur_detail", "description", "annee_experience", "photo_carte_identite",
            "photo_carte_identite_upload", "latitude", "longitude", "profil_verifie",
            "statut_verification", "motif_refus", "date_verification", "specialites", "specialites_detail",
            "zones_intervention", "zones_intervention_detail", "documents_detail", "distance_km",
            "note_moyenne", "nombre_avis",
        )
        read_only_fields = ("utilisateur", "profil_verifie", "statut_verification", "motif_refus", "date_verification", "photo_carte_identite")
