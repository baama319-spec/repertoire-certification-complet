from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from utilisateurs.models import Utilisateur
from reparateurs.models import Reparateur
from .models import Realisation
from .serializers import RealisationSerializer
class RealisationViewSet(ModelViewSet):
    queryset = Realisation.objects.select_related("reparateur").all(); serializer_class = RealisationSerializer
    def get_permissions(self): return [AllowAny()] if self.action in ("list", "retrieve") else [IsAuthenticated()]
    def get_queryset(self):
        qs = super().get_queryset().select_related("reparateur__utilisateur", "specialite")
        reparateur_id = self.request.query_params.get("reparateur")
        if reparateur_id and self.action in ("list", "retrieve"):
            qs = qs.filter(reparateur_id=reparateur_id)
        return qs if self.action in ("list", "retrieve") or self.request.user.role == Utilisateur.Role.ADMINISTRATEUR else qs.filter(reparateur__utilisateur=self.request.user)
    def perform_create(self, serializer):
        try:
            reparateur = Reparateur.objects.get(utilisateur=self.request.user)
        except Reparateur.DoesNotExist:
            raise PermissionDenied("Seul un réparateur peut publier une réalisation.")
        if not reparateur.profil_verifie:
            raise PermissionDenied("Votre profil réparateur doit être vérifié avant de publier.")
        serializer.save(reparateur=reparateur)
