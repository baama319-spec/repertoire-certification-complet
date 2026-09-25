from rest_framework import serializers
from .models import Specialite
class SpecialiteSerializer(serializers.ModelSerializer):
    reparateurs_count = serializers.IntegerField(source="reparateurs.count", read_only=True)
    class Meta: model = Specialite; fields = ("id", "nom", "description", "photo", "actif", "reparateurs_count")
