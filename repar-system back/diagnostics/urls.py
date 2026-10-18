from django.urls import path

from .views import AssistantChatView, DiagnosticView, TranscriptionAudioView, TraductionDescriptionView, VoixAssistantView


urlpatterns = [
    path("assistance/", AssistantChatView.as_view(), name="assistance-chat"),
    path("diagnostic/", DiagnosticView.as_view(), name="diagnostic"),
    path("transcription/", TranscriptionAudioView.as_view(), name="transcription-audio"),
    path("voix/", VoixAssistantView.as_view(), name="voix-assistant"),
    path("traduction/", TraductionDescriptionView.as_view(), name="traduction-description"),
]
