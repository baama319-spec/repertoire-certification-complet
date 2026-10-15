from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DiagnosticRequestSerializer, TranscriptionAudioRequestSerializer
from .services import DiagnosticIAError, DiagnosticIAService, TranscriptionAudioService, TranscriptionIAError


class TranscriptionAudioView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = TranscriptionAudioRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            texte = TranscriptionAudioService().transcrire(serializer.validated_data["audio"])
        except TranscriptionIAError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"text": texte}, status=status.HTTP_200_OK)


class DiagnosticView(APIView):
    permission_classes = [IsAuthenticated]

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
