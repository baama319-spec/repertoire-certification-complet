from rest_framework.viewsets import ModelViewSet
from commun.permissions import EstAdministrateurOuLectureSeule
from .models import Specialite
from .serializers import SpecialiteSerializer
class SpecialiteViewSet(ModelViewSet):
    queryset = Specialite.objects.all().order_by("nom"); serializer_class = SpecialiteSerializer
    permission_classes = [EstAdministrateurOuLectureSeule]
