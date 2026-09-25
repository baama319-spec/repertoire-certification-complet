from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from utilisateurs.models import Utilisateur
from .models import Notification
from .serializers import NotificationSerializer
class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.select_related("utilisateur").all(); serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return super().get_queryset() if self.request.user.role == Utilisateur.Role.ADMINISTRATEUR else super().get_queryset().filter(utilisateur=self.request.user)
    @action(detail=True, methods=["post"])
    def marquer_comme_lue(self, request, pk=None):
        notification = self.get_object(); notification.lue = True; notification.save(update_fields=["lue"])
        return Response(self.get_serializer(notification).data)
