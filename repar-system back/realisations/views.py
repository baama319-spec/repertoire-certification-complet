from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
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
        utilisateur = self.request.user
        if self.action == "mes":
            if not Reparateur.objects.filter(
                utilisateur=utilisateur,
                statut_verification=Reparateur.StatutVerification.VALIDEE,
                utilisateur__actif=True,
            ).exists():
                raise PermissionDenied("Votre candidature réparateur doit être validée par un administrateur.")
            return qs.filter(reparateur__utilisateur=utilisateur)
        if self.action in ("list", "retrieve"):
            if utilisateur.is_authenticated and utilisateur.role == Utilisateur.Role.ADMINISTRATEUR:
                return qs
            qs = qs.filter(
                reparateur__statut_verification=Reparateur.StatutVerification.VALIDEE,
                reparateur__utilisateur__actif=True,
            )
            if utilisateur.is_authenticated and Reparateur.objects.filter(
                utilisateur=utilisateur,
                statut_verification=Reparateur.StatutVerification.VALIDEE,
                utilisateur__actif=True,
            ).exists():
                qs = qs.filter(reparateur__utilisateur=utilisateur)
            elif reparateur_id:
                qs = qs.filter(reparateur_id=reparateur_id)
            return qs
        if utilisateur.role == Utilisateur.Role.ADMINISTRATEUR:
            return qs
        return qs.filter(
            reparateur__utilisateur=utilisateur,
            reparateur__statut_verification=Reparateur.StatutVerification.VALIDEE,
            reparateur__utilisateur__actif=True,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def mes(self, request):
        """Portfolio privé du compte courant, indépendamment de son rôle global."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def perform_create(self, serializer):
        try:
            reparateur = Reparateur.objects.get(utilisateur=self.request.user)
        except Reparateur.DoesNotExist:
            raise PermissionDenied("Seul un réparateur peut publier une réalisation.")
        if reparateur.statut_verification != Reparateur.StatutVerification.VALIDEE or not self.request.user.actif:
            raise PermissionDenied("Votre candidature réparateur doit être validée par un administrateur avant de publier.")
        serializer.save(reparateur=reparateur)
