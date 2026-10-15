from django.urls import path

from .views import DiagnosticView, TranscriptionAudioView


urlpatterns = [
    path("diagnostic/", DiagnosticView.as_view(), name="diagnostic"),
    path("transcription/", TranscriptionAudioView.as_view(), name="transcription-audio"),
]
