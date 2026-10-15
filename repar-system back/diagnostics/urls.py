from django.urls import path

from .views import DiagnosticView, TranscriptionAudioView, TraductionDescriptionView


urlpatterns = [
    path("diagnostic/", DiagnosticView.as_view(), name="diagnostic"),
    path("transcription/", TranscriptionAudioView.as_view(), name="transcription-audio"),
    path("traduction/", TraductionDescriptionView.as_view(), name="traduction-description"),
]
