from rest_framework import serializers


class TranscriptionAudioRequestSerializer(serializers.Serializer):
    audio = serializers.FileField(allow_empty_file=False)
    taille_maximale = 20 * 1024 * 1024
    extensions_autorisees = {".flac", ".m4a", ".mp3", ".mp4", ".mpeg", ".mpga", ".oga", ".ogg", ".wav", ".webm"}

    def validate_audio(self, fichier):
        extension = fichier.name.rsplit(".", 1)[-1].lower() if "." in fichier.name else ""
        if f".{extension}" not in self.extensions_autorisees:
            raise serializers.ValidationError("Format audio non pris en charge. Utilisez WebM, WAV, MP3, M4A ou OGG.")
        if fichier.size > self.taille_maximale:
            raise serializers.ValidationError("L’enregistrement ne doit pas dépasser 20 Mo.")
        return fichier


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
