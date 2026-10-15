from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from diagnostics.services import DiagnosticIAService


class DiagnosticApiTests(APITestCase):
    url = "/api/ia/diagnostic/"

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="client@example.com",
            password="password123",
            nom="Fall",
            prenom="Mamadou",
        )

    def test_diagnostic_requires_authentication(self):
        response = self.client.post(self.url, {"description": "Mon appareil ne démarre plus"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_audio_transcription_requires_authentication(self):
        response = self.client.post(
            "/api/ia/transcription/",
            {"audio": SimpleUploadedFile("voix.webm", b"audio", content_type="audio/webm")},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-token"})
    @patch("diagnostics.services.requests.post")
    def test_audio_transcription_returns_multilingual_text(self, post):
        self.client.force_authenticate(self.user)
        response_from_model = Mock(status_code=200)
        response_from_model.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Téléphone bi daanu, écran bi dafa tas."}]}}]
        }
        post.return_value = response_from_model

        response = self.client.post(
            "/api/ia/transcription/",
            {"audio": SimpleUploadedFile("voix.webm", b"audio", content_type="audio/webm")},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Téléphone bi daanu, écran bi dafa tas.")
        self.assertEqual(
            post.call_args.args[0],
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        )
        self.assertEqual(post.call_args.kwargs["headers"]["x-goog-api-key"], "test-token")
        parts = post.call_args.kwargs["json"]["contents"][0]["parts"]
        self.assertIn("wolof", parts[0]["text"])
        self.assertIn("inlineData", parts[1])

    def test_audio_transcription_rejects_unsupported_file_type(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/ia/transcription/",
            {"audio": SimpleUploadedFile("voix.exe", b"audio", content_type="application/octet-stream")},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("audio", response.data)

    def test_diagnostic_rejects_short_description(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, {"description": "Panne"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-token"})
    @patch("diagnostics.services.requests.post")
    def test_diagnostic_returns_model_json(self, post):
        self.client.force_authenticate(self.user)
        response_from_model = Mock(status_code=200)
        response_from_model.json.return_value = {
            "choices": [{"message": {"content": '{"categorie":"Électronique","specialite":"Téléphonie","probleme_probable":"Défaut de charge","causes_possibles":[],"questions_a_poser":[],"niveau_urgence":"normal","conseils_securite":[],"confiance":0.8,"avertissement":"À confirmer par un réparateur."}'}}]
        }
        post.return_value = response_from_model

        response = self.client.post(
            self.url,
            {
                "appareil": "Téléphone",
                "description": "Le téléphone ne charge plus depuis hier.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["categorie"], "Électronique")
        post.assert_called_once()
        self.assertEqual(post.call_args.args[0], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(post.call_args.kwargs["json"]["model"], "google/gemini-2.5-flash")
        self.assertEqual(post.call_args.kwargs["json"]["provider"], {"sort": "latency"})

    def test_prompt_includes_safety_warning_for_self_repair(self):
        prompt = DiagnosticIAService._prompt_system()

        self.assertIn("professionnel du diagnostic", prompt)
        self.assertIn("réparer", prompt)
        self.assertIn("vous-même", prompt)
        self.assertIn("wolof", prompt)
        self.assertIn("mélange des deux langues", prompt)

    @patch.dict("os.environ", {}, clear=True)
    def test_diagnostic_returns_service_unavailable_when_not_configured(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.url,
            {"description": "Le réfrigérateur ne refroidit plus."},
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-token"})
    @patch("diagnostics.services.requests.post")
    def test_audio_transcription_explains_gemini_quota_limit(self, post):
        self.client.force_authenticate(self.user)
        post.return_value = Mock(status_code=429)

        response = self.client.post(
            "/api/ia/transcription/",
            {"audio": SimpleUploadedFile("voix.webm", b"audio", content_type="audio/webm")},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("quota", response.data["detail"])
