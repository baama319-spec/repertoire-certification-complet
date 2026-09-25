from rest_framework.routers import DefaultRouter
from .views import LocalisationViewSet
router = DefaultRouter(); router.register("", LocalisationViewSet, basename="localisation"); urlpatterns = router.urls
