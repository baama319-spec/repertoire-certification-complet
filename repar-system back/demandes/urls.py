from rest_framework.routers import DefaultRouter
from .views import DemandeViewSet, PieceJointeViewSet
router = DefaultRouter(); router.register("", DemandeViewSet, basename="demande"); router.register("pieces-jointes", PieceJointeViewSet, basename="piece-jointe"); urlpatterns = router.urls
