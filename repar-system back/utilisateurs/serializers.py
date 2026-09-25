from rest_framework import serializers
from django.db import transaction
from PIL import Image, UnidentifiedImageError
from clients.models import Client
from localisations.models import Localisation
from .models import Utilisateur

class UtilisateurSerializer(serializers.ModelSerializer):
    photo_profil = serializers.SerializerMethodField(read_only=True)
    photo_profil_upload = serializers.ImageField(write_only=True, required=False, source="photo_profil")
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    profil_reparateur = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Utilisateur
        fields = ("id", "email", "password", "nom", "prenom", "telephone", "photo_profil", "photo_profil_upload", "role", "actif", "date_inscription", "profil_reparateur")
        read_only_fields = ("id", "date_inscription")
    def validate_role(self, value):
        request = self.context.get("request")
        if value != Utilisateur.Role.CLIENT and not (request and request.user.is_staff):
            raise serializers.ValidationError("Seul un administrateur peut attribuer ce rôle.")
        return value

    def validate_photo_profil_upload(self, fichier):
        formats_acceptes = {"JPEG", "PNG", "WEBP"}
        types_acceptes = {"image/jpeg", "image/png", "image/webp"}
        taille_max = 5 * 1024 * 1024
        if fichier.size > taille_max:
            raise serializers.ValidationError("La photo ne doit pas dépasser 5 Mo.")
        if getattr(fichier, "content_type", "") not in types_acceptes:
            raise serializers.ValidationError("Utilisez une image JPG, PNG ou WEBP.")
        try:
            image = Image.open(fichier)
            image.verify()
            if image.format not in formats_acceptes:
                raise serializers.ValidationError("Utilisez une image JPG, PNG ou WEBP.")
        except (UnidentifiedImageError, OSError, ValueError):
            raise serializers.ValidationError("Le fichier envoyé n'est pas une image valide.")
        finally:
            fichier.seek(0)
        return fichier

    def get_photo_profil(self, utilisateur):
        if not utilisateur.photo_profil:
            return None
        url = utilisateur.photo_profil.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_profil_reparateur(self, utilisateur):
        profil = getattr(utilisateur, "profil_reparateur", None)
        if not profil:
            return None
        return {"id": profil.id, "statut_verification": profil.statut_verification, "profil_verifie": profil.profil_verifie}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = Utilisateur(**validated_data)
        if password: user.set_password(password)
        else: user.set_unusable_password()
        user.save()
        return user
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        ancienne_photo = instance.photo_profil if "photo_profil" in validated_data else None
        for attr, value in validated_data.items(): setattr(instance, attr, value)
        if password: instance.set_password(password)
        instance.save()
        if ancienne_photo and ancienne_photo.name != instance.photo_profil.name:
            ancienne_photo.storage.delete(ancienne_photo.name)
        return instance


class InscriptionSerializer(UtilisateurSerializer):
    zone_residence = serializers.PrimaryKeyRelatedField(queryset=Localisation.objects.filter(actif=True), write_only=True, required=False, allow_null=True)
    adresse_principale = serializers.CharField(max_length=255, required=False, allow_blank=True, write_only=True)
    class Meta(UtilisateurSerializer.Meta):
        fields = ("id", "email", "password", "nom", "prenom", "telephone", "zone_residence", "adresse_principale")
        read_only_fields = ("id",)

    def create(self, validated_data):
        zone_residence = validated_data.pop("zone_residence", None)
        adresse_principale = validated_data.pop("adresse_principale", "")
        validated_data["role"] = Utilisateur.Role.CLIENT
        # Chaque inscription publique correspond à un compte client utilisable
        # immédiatement par les ressources métier (demandes, avis, etc.).
        with transaction.atomic():
            utilisateur = super().create(validated_data)
            Client.objects.create(utilisateur=utilisateur, zone_residence=zone_residence, adresse_principale=adresse_principale)
        return utilisateur
