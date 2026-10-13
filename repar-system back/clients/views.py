from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.authtoken.models import Token
from utilisateurs.models import Utilisateur
from .models import Client
from .serializers import ClientSerializer

class ClientViewSet(ModelViewSet):
    queryset = Client.objects.select_related("utilisateur", "zone_residence").all(); serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset if self.request.user.role == Utilisateur.Role.ADMINISTRATEUR else queryset.filter(utilisateur=self.request.user)

    @action(detail=True, methods=["post"])
    def bloquer(self, request, pk=None):
        if request.user.role != Utilisateur.Role.ADMINISTRATEUR:
            raise PermissionDenied("Seul un administrateur peut bloquer un client.")
        client = self.get_object()
        utilisateur = client.utilisateur
        bloquer = request.data.get("bloquer", True)
        if not isinstance(bloquer, bool):
            return Response({"bloquer": ["La valeur doit être booléenne."]}, status=status.HTTP_400_BAD_REQUEST)
        utilisateur.actif = not bloquer
        utilisateur.save(update_fields=("actif",))
        if bloquer:
            Token.objects.filter(user=utilisateur).delete()
        return Response(self.get_serializer(client).data)
