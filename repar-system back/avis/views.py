from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from notifications.models import Notification
from notifications.services import envoyer_notification_n8n
from utilisateurs.models import Utilisateur
from .models import Avis
from .serializers import AvisSerializer


class AvisViewSet(ModelViewSet):
    queryset = Avis.objects.select_related(
        "client__utilisateur",
        "reparateur__utilisateur",
        "demande__specialite",
        "demande__localisation",
    ).all()
    serializer_class = AvisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == Utilisateur.Role.ADMINISTRATEUR:
            return qs
        if user.role == Utilisateur.Role.CLIENT:
            return qs.filter(client__utilisateur=user)
        return qs.filter(reparateur__utilisateur=user)

    def perform_create(self, serializer):
        if self.request.user.role != Utilisateur.Role.CLIENT:
            raise PermissionDenied("Seul un client peut laisser un avis.")

        avis = serializer.save()
        demande = avis.demande
        if demande.reparateur and demande.reparateur.utilisateur:
            message = (
                f"Un client a laissé un avis pour votre demande #{demande.pk}. "
                f"Note: {avis.note}/5."
            )
            Notification.objects.create(
                utilisateur=demande.reparateur.utilisateur,
                titre="Nouvel avis",
                message=message,
                type=Notification.Type.NOUVEL_AVIS,
            )
            envoyer_notification_n8n(
                demande.reparateur.utilisateur,
                "Nouvel avis",
                message,
                "nouvel_avis",
            )
