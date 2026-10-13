from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import DashboardView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("admin/", admin.site.urls),
    path("api/utilisateurs/", include("utilisateurs.urls")),
    path("api/reparateurs/", include("reparateurs.urls")),
    path("api/clients/", include("clients.urls")),
    path("api/demandes/", include("demandes.urls")),
    path("api/specialites/", include("specialites.urls")),
    path("api/localisations/", include("localisations.urls")),
    path("api/realisations/", include("realisations.urls")),
    path("api/avis/", include("avis.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/ia/", include("diagnostics.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
