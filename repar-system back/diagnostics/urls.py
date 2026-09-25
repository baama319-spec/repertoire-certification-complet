from django.urls import path

from .views import DiagnosticView


urlpatterns = [
    path("diagnostic/", DiagnosticView.as_view(), name="diagnostic"),
]
