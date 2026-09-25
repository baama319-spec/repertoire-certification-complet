from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DiagnosticRequestSerializer
from .services import DiagnosticIAError, DiagnosticIAService


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
