from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.views import APIView

from .serializers import AssistantChatRequestSerializer, DiagnosticRequestSerializer, TranscriptionAudioRequestSerializer, TraductionDescriptionSerializer, VoixAssistantRequestSerializer
from .services import (
    AssistantConversationService,
    DiagnosticIAError,
    DiagnosticIAService,
    TranscriptionAudioService,
    TranscriptionIAError,
    TraductionDiagnosticService,
    TraductionIAError,
    VoixAssistantService,
    VoixIAError,
)


class TraductionDescriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TraductionDescriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            traduction = TraductionDiagnosticService().traduire(serializer.validated_data["description"])
        except TraductionIAError as error:
            return Response({"detail": str(error)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({"description_francaise": traduction}, status=status.HTTP_200_OK)


class TranscriptionAudioView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = TranscriptionAudioRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            texte = TranscriptionAudioService().transcrire(
                serializer.validated_data["audio"],
                serializer.validated_data["language"],
            )
        except TranscriptionIAError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"text": texte}, status=status.HTTP_200_OK)


class VoixAssistantView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = VoixAssistantRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            audio = VoixAssistantService().generer(
                serializer.validated_data["text"],
                serializer.validated_data["language"],
            )
        except VoixIAError as error:
            return Response({"detail": str(error)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return HttpResponse(audio, content_type="audio/mpeg")


class DiagnosticView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        serializer = DiagnosticRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            diagnostic = DiagnosticIAService().analyser(serializer.validated_data)
        except DiagnosticIAError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(diagnostic, status=status.HTTP_200_OK)


class AssistantChatView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        if hasattr(request.data, "dict"):
            donnees = request.data.dict()
            if request.FILES:
                donnees["photos"] = request.FILES.getlist("photos")
        else:
            donnees = request.data
        if isinstance(donnees.get("messages"), str):
            import json
            try:
                donnees["messages"] = json.loads(donnees["messages"])
            except (TypeError, ValueError):
                return Response({"messages": ["Format de conversation invalide."]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AssistantChatRequestSerializer(data=donnees)
        serializer.is_valid(raise_exception=True)
        try:
            reponse = AssistantConversationService().repondre(
                serializer.validated_data["messages"],
                serializer.validated_data.get("language", "auto"),
                serializer.validated_data.get("photos", []),
            )
        except DiagnosticIAError as error:
            return Response({"detail": str(error)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"reply": reponse}, status=status.HTTP_200_OK)
