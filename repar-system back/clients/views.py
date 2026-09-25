from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from utilisateurs.models import Utilisateur
from .models import Client
from .serializers import ClientSerializer
class ClientViewSet(ModelViewSet):
    queryset = Client.objects.select_related("utilisateur", "zone_residence").all(); serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset if self.request.user.role == Utilisateur.Role.ADMINISTRATEUR else queryset.filter(utilisateur=self.request.user)
