from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from clients.models import Client
from demandes.models import DemandeMiseEnRelation
from utilisateurs.models import Utilisateur
from .models import Avis


class AvisSerializer(serializers.ModelSerializer):
    client_nom = serializers.SerializerMethodField()
    client_photo = serializers.SerializerMethodField()
    reparateur_nom = serializers.SerializerMethodField()
    demande_appareil = serializers.CharField(source="demande.appareil", read_only=True)
    demande_specialite = serializers.CharField(source="demande.specialite.nom", read_only=True, default="Réparation générale")
    demande_localisation = serializers.SerializerMethodField()

    class Meta:
        model = Avis
        fields = [
            "id", "demande", "client", "reparateur", "note", "commentaire", "date_creation",
            "client_nom", "client_photo", "reparateur_nom", "demande_appareil", "demande_specialite", "demande_localisation",
        ]
        read_only_fields = ["client", "reparateur", "date_creation"]

    def get_client_nom(self, obj):
        utilisateur = obj.client.utilisateur
        return f"{utilisateur.prenom} {utilisateur.nom}".strip()

    def get_client_photo(self, obj):
        photo = obj.client.utilisateur.photo_profil
        return photo.url if photo else None

    def get_reparateur_nom(self, obj):
        utilisateur = obj.reparateur.utilisateur
        return f"{utilisateur.prenom} {utilisateur.nom}".strip()

    def get_demande_localisation(self, obj):
        localisation = obj.demande.localisation
        return ", ".join(part for part in (localisation.ville, localisation.quartier or localisation.nom) if part)

    def validate_note(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("La note doit être comprise entre 1 et 5.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        demande = attrs.get("demande")

        if request is None or getattr(request.user, "role", None) != Utilisateur.Role.CLIENT:
            raise serializers.ValidationError("Seul un client peut laisser un avis.")

        if demande is None:
            raise serializers.ValidationError({"demande": "Une demande est obligatoire."})

        if demande.statut != DemandeMiseEnRelation.Statut.ACCEPTEE:
            raise serializers.ValidationError("Un avis ne peut être donné que pour une demande acceptée.")

        client = Client.objects.filter(utilisateur=request.user).first()
        if client is None:
            raise serializers.ValidationError("Le compte courant n’a pas de profil client.")

        if demande.client_id != client.pk:
            raise serializers.ValidationError("Vous ne pouvez laisser un avis que sur votre propre demande.")

        if hasattr(demande, "avis"):
            raise serializers.ValidationError("Une seule note est autorisée pour cette demande.")

        attrs["client"] = client
        attrs["reparateur"] = demande.reparateur
        return attrs

    def create(self, validated_data):
        client = validated_data.pop("client")
        reparateur = validated_data.pop("reparateur")
        avis = Avis.objects.create(client=client, reparateur=reparateur, **validated_data)
        return avis
