from rest_framework import serializers
from .models import Avis
class AvisSerializer(serializers.ModelSerializer):
    class Meta: model = Avis; fields = "__all__"; read_only_fields = ("date_creation",)
    def validate_note(self, value):
        if not 1 <= value <= 5: raise serializers.ValidationError("La note doit être comprise entre 1 et 5.")
        return value
