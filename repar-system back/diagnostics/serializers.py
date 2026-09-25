from rest_framework import serializers


class DiagnosticRequestSerializer(serializers.Serializer):
    appareil = serializers.CharField(max_length=150, required=False, allow_blank=True)
    marque = serializers.CharField(max_length=150, required=False, allow_blank=True)
    description = serializers.CharField(max_length=3000)
    ville = serializers.CharField(max_length=100, required=False, allow_blank=True)
    quartier = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_description(self, value):
        description = " ".join(value.split())
        if len(description) < 10:
            raise serializers.ValidationError(
                "Décrivez le problème avec au moins 10 caractères."
            )
        return description
