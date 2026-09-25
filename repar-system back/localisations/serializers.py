from rest_framework import serializers
from .models import Localisation
class LocalisationSerializer(serializers.ModelSerializer):
    reparateurs_count = serializers.IntegerField(source="reparateurs_intervenants.count", read_only=True)
    class Meta: model = Localisation; fields = ("id", "nom", "adresse", "quartier", "ville", "actif", "reparateurs_count")
