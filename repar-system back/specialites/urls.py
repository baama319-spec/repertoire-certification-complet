from rest_framework.routers import DefaultRouter
from .views import SpecialiteViewSet
router = DefaultRouter(); router.register("", SpecialiteViewSet, basename="specialite"); urlpatterns = router.urls
