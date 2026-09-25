from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import Realisation
class RealisationSerializer(ModelSerializer):
    reparateur_nom = serializers.SerializerMethodField(read_only=True)
    specialite_nom = serializers.CharField(source="specialite.nom", read_only=True)
    photo_avant_url = serializers.SerializerMethodField(read_only=True)
    photo_apres_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Realisation
        fields = "__all__"
        read_only_fields = ("reparateur", "date_realisation", "photo",)

    def get_reparateur_nom(self, realisation):
        utilisateur = realisation.reparateur.utilisateur
        return f"{utilisateur.prenom} {utilisateur.nom}".strip()

    def _url(self, fichier):
        if not fichier:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(fichier.url) if request else fichier.url

    def get_photo_avant_url(self, realisation): return self._url(realisation.photo_avant)
    def get_photo_apres_url(self, realisation): return self._url(realisation.photo_apres or realisation.photo)

    def validate(self, attrs):
        if self.instance is None and not attrs.get("specialite"):
            raise serializers.ValidationError({"specialite": "Ce champ est obligatoire."})
        return attrs
