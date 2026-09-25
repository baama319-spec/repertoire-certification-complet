from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from utilisateurs.models import Utilisateur
from clients.models import Client
from notifications.models import Notification
from .models import DemandeMiseEnRelation, PieceJointe
from .serializers import DemandeSerializer, PieceJointeSerializer
class DemandeViewSet(ModelViewSet):
    queryset = DemandeMiseEnRelation.objects.select_related("client", "reparateur", "localisation", "specialite").all()
    serializer_class = DemandeSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == Utilisateur.Role.ADMINISTRATEUR: return qs
        if user.role == Utilisateur.Role.CLIENT: return qs.filter(client__utilisateur=user)
        return qs.filter(reparateur__utilisateur=user)
    def perform_create(self, serializer):
        if self.request.user.role != Utilisateur.Role.CLIENT:
            raise PermissionDenied("Seul un client peut créer une demande.")
        client = Client.objects.filter(utilisateur=self.request.user).first()
        if client is None:
            raise PermissionDenied("Le compte courant ne possède pas de profil client.")
        serializer.save(client=client)
    @action(detail=True, methods=["post"])
    def accepter(self, request, pk=None):
        demande = self.get_object()
        if request.user.role != Utilisateur.Role.REPARATEUR or demande.reparateur.utilisateur_id != request.user.id:
            return Response({"detail": "Action non autorisée."}, status=403)
        demande.statut = DemandeMiseEnRelation.Statut.ACCEPTEE; demande.date_reponse = timezone.now(); demande.save(update_fields=["statut", "date_reponse"])
        Notification.objects.create(utilisateur=demande.client.utilisateur, titre="Demande acceptée", message="Votre demande a été acceptée.", type=Notification.Type.DEMANDE_ACCEPTEE)
        return Response(self.get_serializer(demande).data)
    @action(detail=True, methods=["post"])
    def refuser(self, request, pk=None):
        demande = self.get_object()
        if request.user.role != Utilisateur.Role.REPARATEUR or demande.reparateur.utilisateur_id != request.user.id:
            return Response({"detail": "Action non autorisée."}, status=403)
        demande.statut = DemandeMiseEnRelation.Statut.REFUSEE; demande.date_reponse = timezone.now(); demande.save(update_fields=["statut", "date_reponse"])
        Notification.objects.create(utilisateur=demande.client.utilisateur, titre="Demande refusée", message="Votre demande ne peut pas être prise en charge.", type=Notification.Type.DEMANDE_REFUSEE)
        return Response(self.get_serializer(demande).data)
class PieceJointeViewSet(ModelViewSet):
    queryset = PieceJointe.objects.select_related("demande").all(); serializer_class = PieceJointeSerializer
