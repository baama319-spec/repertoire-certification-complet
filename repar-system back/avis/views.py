from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from utilisateurs.models import Utilisateur
from .models import Avis
from .serializers import AvisSerializer
class AvisViewSet(ModelViewSet):
    queryset = Avis.objects.select_related("client", "reparateur", "demande").all(); serializer_class = AvisSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = super().get_queryset(); user = self.request.user
        if user.role == Utilisateur.Role.ADMINISTRATEUR: return qs
        if user.role == Utilisateur.Role.CLIENT: return qs.filter(client__utilisateur=user)
        return qs.filter(reparateur__utilisateur=user)
