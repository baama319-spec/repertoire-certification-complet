from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from commun.permissions import EstAdministrateur
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
    ).prefetch_related("pieces_jointes").all()
    serializer_class = DemandeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        photos = request.FILES.getlist("photos")
        if len(photos) > 3:
            return Response(
                {"photos": ["Vous pouvez joindre jusqu'à 3 photos maximum."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == Utilisateur.Role.ADMINISTRATEUR: return qs
        action_reparateur = self.action in {"accepter", "refuser"}
        if self.request.query_params.get("contexte") == "reparateur" or action_reparateur:
            profil = Reparateur.objects.filter(
                utilisateur=user,
                statut_verification=Reparateur.StatutVerification.VALIDEE,
                utilisateur__actif=True,
            ).exists()
            if not profil:
                raise PermissionDenied("Votre candidature réparateur doit être validée par un administrateur.")
            return qs.filter(
                reparateur__utilisateur=user,
                reparateur__statut_verification=Reparateur.StatutVerification.VALIDEE,
                reparateur__utilisateur__actif=True,
            )
        if user.role == Utilisateur.Role.CLIENT: return qs.filter(client__utilisateur=user)
        return qs.filter(
            reparateur__utilisateur=user,
            reparateur__statut_verification=Reparateur.StatutVerification.VALIDEE,
            reparateur__utilisateur__actif=True,
        )

    @action(detail=False, methods=["get"], permission_classes=[EstAdministrateur])
    def statistiques(self, request):
        """Indicateurs agrégés destinés exclusivement au tableau de bord admin."""
        from django.db.models import Count
        from clients.models import Client
        from localisations.models import Localisation

        demandes = self.queryset
        total_demandes = demandes.count()
        demandes_acceptees = demandes.filter(
            statut=DemandeMiseEnRelation.Statut.ACCEPTEE
        ).count()
        reparateurs_actifs = Reparateur.objects.filter(
            statut_verification=Reparateur.StatutVerification.VALIDEE,
            utilisateur__actif=True,
        ).count()

        repartition = (
            demandes.values("specialite__nom")
            .annotate(count=Count("id"))
            .order_by("-count", "specialite__nom")
        )
        return Response({
            "clients_inscrits": Client.objects.count(),
            "reparateurs_actifs": reparateurs_actifs,
            "demandes_totales": total_demandes,
            "zones_couvertes": Localisation.objects.filter(actif=True).count(),
            "demandes_acceptees": demandes_acceptees,
            "taux_acceptation": round(
                (demandes_acceptees / total_demandes * 100) if total_demandes else 0,
                1,
            ),
            "repartition_demandes": [
                {
                    "nom": item["specialite__nom"] or "Sans spécialité",
                    "nombre": item["count"],
                }
                for item in repartition
            ],
        })
    def perform_create(self, serializer):
        if self.request.user.role != Utilisateur.Role.CLIENT:
            raise PermissionDenied("Seul un client peut créer une demande.")
        client = Client.objects.filter(utilisateur=self.request.user).first()
        if client is None:
            raise PermissionDenied("Le compte courant ne possède pas de profil client.")
        demande = serializer.save(client=client)

        photos = self.request.FILES.getlist("photos")
        for fichier in photos[:3]:
            PieceJointe.objects.create(
                demande=demande,
                nom_fichier=fichier.name,
                fichier=fichier,
                type="PHOTO",
            )

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

    @action(detail=True, methods=["post"], url_path="annuler")
    def annuler(self, request, pk=None):
        """Permet au client propriétaire d'annuler une demande encore en attente."""
        demande = self.get_object()
        if request.user.role != Utilisateur.Role.CLIENT or demande.client.utilisateur_id != request.user.id:
            return Response({"detail": "Vous ne pouvez pas annuler cette demande."}, status=status.HTTP_403_FORBIDDEN)
        if demande.statut != DemandeMiseEnRelation.Statut.EN_ATTENTE:
            return Response({"detail": "Seules les demandes en attente peuvent être annulées."}, status=status.HTTP_400_BAD_REQUEST)
        demande.statut = DemandeMiseEnRelation.Statut.ANNULEE
        demande.date_reponse = timezone.now()
        demande.save(update_fields=["statut", "date_reponse"])
        if demande.reparateur_id:
            Notification.objects.create(
                utilisateur=demande.reparateur.utilisateur,
                titre="Demande annulée par le client",
                message=f"Le client a annulé la demande de réparation #{demande.pk}.",
                type=Notification.Type.SYSTEME,
            )
        return Response(self.get_serializer(demande).data)

    def _autoriser_reparateur_assigne(self, request, demande):
        profil = Reparateur.objects.filter(utilisateur=request.user).first()
        return bool(
            profil
            and profil.statut_verification == Reparateur.StatutVerification.VALIDEE
            and request.user.actif
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
