from rest_framework.viewsets import ModelViewSet
from commun.permissions import EstAdministrateurOuLectureSeule
from .models import Localisation
from .serializers import LocalisationSerializer
class LocalisationViewSet(ModelViewSet):
    queryset = Localisation.objects.all().order_by("ville"); serializer_class = LocalisationSerializer
    permission_classes = [EstAdministrateurOuLectureSeule]
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset if self.request.user.is_authenticated and self.request.user.role == "ADMINISTRATEUR" else queryset.filter(actif=True)
