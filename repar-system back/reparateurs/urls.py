from rest_framework.routers import DefaultRouter
from .views import ReparateurViewSet
router = DefaultRouter(); router.register("", ReparateurViewSet, basename="reparateur"); urlpatterns = router.urls
