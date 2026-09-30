from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from utilisateurs.models import Utilisateur
from clients.models import Client
from reparateurs.models import Reparateur
from notifications.models import Notification
from notifications.services import envoyer_notification_n8n
from .models import DemandeMiseEnRelation, PieceJointe
from .serializers import DemandeSerializer, PieceJointeSerializer
class DemandeViewSet(ModelViewSet):
    queryset = DemandeMiseEnRelation.objects.select_related(
        "client__utilisateur", "reparateur__utilisateur", "localisation", "specialite"
    ).all()
    serializer_class = DemandeSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == Utilisateur.Role.ADMINISTRATEUR: return qs
        action_reparateur = self.action in {"accepter", "refuser"}
        if self.request.query_params.get("contexte") == "reparateur" or action_reparateur:
            if not hasattr(user, "profil_reparateur"):
                raise PermissionDenied("Aucun profil réparateur n’est associé à ce compte.")
            return qs.filter(reparateur__utilisateur=user)
        if user.role == Utilisateur.Role.CLIENT: return qs.filter(client__utilisateur=user)
        return qs.filter(reparateur__utilisateur=user)
    def perform_create(self, serializer):
        if self.request.user.role != Utilisateur.Role.CLIENT:
            raise PermissionDenied("Seul un client peut créer une demande.")
        client = Client.objects.filter(utilisateur=self.request.user).first()
        if client is None:
            raise PermissionDenied("Le compte courant ne possède pas de profil client.")
        demande = serializer.save(client=client)

        # Une demande ciblant un réparateur le prévient à la fois dans
        # l'application et par le workflow e-mail n8n existant.
        if demande.reparateur_id:
            reparateur = demande.reparateur.utilisateur
            titre = "Nouvelle demande de réparation"
            message = "Un client vous a envoyé une nouvelle demande de réparation."
            Notification.objects.create(
                utilisateur=reparateur,
                titre=titre,
                message=message,
                type=Notification.Type.NOUVELLE_DEMANDE,
            )
            envoyer_notification_n8n(
                reparateur,
                titre,
                message,
                "nouvelle_demande",
            )

    def _autoriser_reparateur_assigne(self, request, demande):
        profil = Reparateur.objects.filter(utilisateur=request.user).first()
        return bool(
            profil
            and request.user.role in (Utilisateur.Role.REPARATEUR, Utilisateur.Role.CLIENT)
            and demande.reparateur_id == profil.id
        )

    @action(detail=True, methods=["post"])
    def accepter(self, request, pk=None):
        demande = self.get_object()
        if not self._autoriser_reparateur_assigne(request, demande):
            return Response({"detail": "Action non autorisée."}, status=403)
        if demande.statut != DemandeMiseEnRelation.Statut.EN_ATTENTE:
            return Response({"detail": "Cette demande a déjà reçu une réponse."}, status=400)
        demande.statut = DemandeMiseEnRelation.Statut.ACCEPTEE; demande.date_reponse = timezone.now(); demande.save(update_fields=["statut", "date_reponse"])
        Notification.objects.create(utilisateur=demande.client.utilisateur, titre="Demande acceptée", message="Votre demande a été acceptée.", type=Notification.Type.DEMANDE_ACCEPTEE)
        envoyer_notification_n8n(
            demande.client.utilisateur,
            "Demande acceptée",
            "Votre demande a été acceptée.",
            "demande_acceptee",
        )
        return Response(self.get_serializer(demande).data)
    @action(detail=True, methods=["post"])
    def refuser(self, request, pk=None):
        demande = self.get_object()
        if not self._autoriser_reparateur_assigne(request, demande):
            return Response({"detail": "Action non autorisée."}, status=403)
        if demande.statut != DemandeMiseEnRelation.Statut.EN_ATTENTE:
            return Response({"detail": "Cette demande a déjà reçu une réponse."}, status=400)
        demande.statut = DemandeMiseEnRelation.Statut.REFUSEE; demande.date_reponse = timezone.now(); demande.save(update_fields=["statut", "date_reponse"])
        Notification.objects.create(utilisateur=demande.client.utilisateur, titre="Demande refusée", message="Votre demande ne peut pas être prise en charge.", type=Notification.Type.DEMANDE_REFUSEE)
        envoyer_notification_n8n(
            demande.client.utilisateur,
            "Demande refusée",
            "Votre demande ne peut pas être prise en charge.",
            "demande_refusee",
        )
        return Response(self.get_serializer(demande).data)
class PieceJointeViewSet(ModelViewSet):
    queryset = PieceJointe.objects.select_related("demande").all(); serializer_class = PieceJointeSerializer
