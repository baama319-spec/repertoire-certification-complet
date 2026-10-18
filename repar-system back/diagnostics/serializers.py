from rest_framework import serializers


class TranscriptionAudioRequestSerializer(serializers.Serializer):
    audio = serializers.FileField(allow_empty_file=False)
    language = serializers.ChoiceField(choices=("auto", "fr", "wo"), default="auto")
    taille_maximale = 20 * 1024 * 1024
    extensions_autorisees = {".flac", ".mp3", ".wav"}

    def validate_audio(self, fichier):
        extension = fichier.name.rsplit(".", 1)[-1].lower() if "." in fichier.name else ""
        if f".{extension}" not in self.extensions_autorisees:
            raise serializers.ValidationError("Format audio non pris en charge. Le serveur attend un fichier WAV, MP3 ou FLAC.")
        if fichier.size > self.taille_maximale:
            raise serializers.ValidationError("L’enregistrement ne doit pas dépasser 20 Mo.")
        return fichier


class VoixAssistantRequestSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=3000, trim_whitespace=True)
    language = serializers.ChoiceField(choices=("fr", "wo"), default="fr")


class TraductionDescriptionSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=3000)

    def validate_description(self, value):
        description = " ".join(value.split())
        if len(description) < 10:
            raise serializers.ValidationError("Décrivez le problème avec au moins 10 caractères.")
        return description


class DiagnosticRequestSerializer(serializers.Serializer):
    appareil = serializers.CharField(max_length=150, required=False, allow_blank=True)
    marque = serializers.CharField(max_length=150, required=False, allow_blank=True)
    description = serializers.CharField(max_length=3000)
    ville = serializers.CharField(max_length=100, required=False, allow_blank=True)
    quartier = serializers.CharField(max_length=100, required=False, allow_blank=True)
    photos = serializers.ListField(
        child=serializers.ImageField(), required=False, max_length=3,
    )

    def validate_photos(self, photos):
        taille_maximale = 5 * 1024 * 1024
        formats_acceptes = {"JPEG", "PNG", "WEBP"}
        for photo in photos:
            if photo.size > taille_maximale:
                raise serializers.ValidationError("Chaque photo doit faire 5 Mo maximum.")
            if getattr(photo, "image", None) and photo.image.format not in formats_acceptes:
                raise serializers.ValidationError("Utilisez des photos JPG, PNG ou WEBP.")
        return photos

    def validate_description(self, value):
        description = " ".join(value.split())
        if len(description) < 10:
            raise serializers.ValidationError(
                "Décrivez le problème avec au moins 10 caractères."
            )
        return description


class AssistantChatRequestSerializer(serializers.Serializer):
    messages = serializers.ListField(
        child=serializers.DictField(), min_length=1, max_length=12,
    )
    language = serializers.ChoiceField(choices=("auto", "fr", "wo"), default="auto")
    photos = serializers.ListField(child=serializers.ImageField(), required=False, max_length=3)

    def validate_messages(self, messages):
        for message in messages:
            if set(message) != {"role", "content"}:
                raise serializers.ValidationError("Chaque message doit contenir un rôle et un texte.")
            if message["role"] not in {"user", "assistant"}:
                raise serializers.ValidationError("Rôle de message non valide.")
            if not isinstance(message["content"], str) or not message["content"].strip():
                raise serializers.ValidationError("Le texte d’un message ne peut pas être vide.")
            if len(message["content"]) > 3000:
                raise serializers.ValidationError("Un message ne peut pas dépasser 3000 caractères.")
        if messages[-1]["role"] != "user":
            raise serializers.ValidationError("Le dernier message doit venir de l’utilisateur.")
        return messages

    def validate_photos(self, photos):
        for photo in photos:
            if photo.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Chaque photo doit faire 5 Mo maximum.")
            if getattr(photo, "image", None) and photo.image.format not in {"JPEG", "PNG", "WEBP"}:
                raise serializers.ValidationError("Utilisez des photos JPG, PNG ou WEBP.")
        return photos
