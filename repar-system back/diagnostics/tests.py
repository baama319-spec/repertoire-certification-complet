from unittest.mock import Mock, patch
from io import BytesIO
import json

from PIL import Image

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from diagnostics.services import AssistantConversationService, DiagnosticIAService


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

    @patch("diagnostics.services.TranscriptionAudioService.transcrire", return_value="Mon téléphone ne démarre plus.")
    def test_audio_transcription_is_available_without_authentication(self, transcrire):
        response = self.client.post(
            "/api/ia/transcription/",
            {"audio": SimpleUploadedFile("voix.wav", b"RIFFfake", content_type="audio/wav")},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Mon téléphone ne démarre plus.")
        transcrire.assert_called_once()

    @patch("diagnostics.services.VoixAssistantService.generer", return_value=b"fake-mp3")
    def test_assistant_voice_returns_soynade_audio(self, generer):
        response = self.client.post(
            "/api/ia/voix/",
            {"text": "Bonjour, comment puis-je vous aider ?", "language": "fr"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "audio/mpeg")
        self.assertEqual(response.content, b"fake-mp3")
        generer.assert_called_once_with("Bonjour, comment puis-je vous aider ?", "fr")

    @patch.dict("os.environ", {"SOYNADE_API_KEY": "test-soynade-key"})
    @patch("diagnostics.services.requests.post")
    def test_soynade_voice_uses_api_key_and_wolof_language(self, post):
        from diagnostics.services import VoixAssistantService

        post.return_value = Mock(status_code=200, content=b"fake-mp3")
        audio = VoixAssistantService().generer("Naka nga def?", "wo")

        self.assertEqual(audio, b"fake-mp3")
        self.assertEqual(post.call_args.args[0], "https://api.soynade.ai/v1/text-to-speech")
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer test-soynade-key")
        self.assertEqual(post.call_args.kwargs["json"]["language"], "wo")
        self.assertEqual(post.call_args.kwargs["json"]["output_format"], "mp3")

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-token"})
    @patch("diagnostics.services.requests.post")
    def test_assistant_chat_responds_to_anonymous_wolof_conversation(self, post):
        response_from_model = Mock(status_code=200)
        response_from_model.json.return_value = {"choices": [{"message": {"content": "Naka la téléphone bi di doxee ?"}}]}
        post.return_value = response_from_model

        response = self.client.post(
            "/api/ia/assistance/",
            {
                "language": "wo",
                "messages": [{"role": "user", "content": "Téléphone bi dafa doxul."}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["reply"], "Naka la téléphone bi di doxee ?")
        messages = post.call_args.kwargs["json"]["messages"]
        self.assertIn("Réponds toujours en wolof", messages[0]["content"])
        self.assertIn("40 mots maximum", messages[0]["content"])
        self.assertIn("une seule vérification", messages[0]["content"])
        self.assertEqual(post.call_args.kwargs["json"]["max_tokens"], 220)
        self.assertEqual(messages[1]["content"], "Téléphone bi dafa doxul.")

    def test_assistant_prompt_requires_short_step_by_step_answers(self):
        prompt = AssistantConversationService._prompt_system("wo")

        self.assertIn("40 mots maximum", prompt)
        self.assertIn("une seule vérification", prompt)
        self.assertIn("Ne répète pas le même message dans deux langues", prompt)
        self.assertIn("au plus 2 petites étapes", prompt)

    def test_assistant_rejects_conversation_ending_with_assistant(self):
        response = self.client.post(
            "/api/ia/assistance/",
            {"messages": [{"role": "assistant", "content": "Bonjour."}]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("messages", response.data)

    def test_translation_requires_authentication(self):
        response = self.client.post(
            "/api/ia/traduction/",
            {"description": "Téléphone bi dafa doy waar."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-token"})
    @patch("diagnostics.services.requests.post")
    def test_translation_returns_french_and_preserves_technical_meaning(self, post):
        self.client.force_authenticate(self.user)
        response_from_model = Mock(status_code=200)
        response_from_model.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Le téléphone chauffe beaucoup."}]}}]
        }
        post.return_value = response_from_model

        response = self.client.post(
            "/api/ia/traduction/",
            {"description": "Téléphone bi dafa doy waar."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description_francaise"], "Le téléphone chauffe beaucoup.")
        self.assertIn("wolof", post.call_args.kwargs["json"]["contents"][0]["parts"][0]["text"])
        self.assertIn("/gemini-3.6-flash:generateContent", post.call_args.args[0])

    def test_translation_rejects_short_description(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/ia/traduction/",
            {"description": "Panne"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)

    @patch.dict("os.environ", {"SOYNADE_API_KEY": "test-soynade-key"})
    @patch("diagnostics.services.requests.post")
    def test_audio_transcription_uses_soynade_and_returns_wolof_text(self, post):
        response_from_provider = Mock(status_code=200)
        response_from_provider.json.return_value = {"text": "Téléphone bi daanu, écran bi dafa tas."}
        post.return_value = response_from_provider

        response = self.client.post(
            "/api/ia/transcription/",
            {
                "audio": SimpleUploadedFile("voix.wav", b"RIFFfake", content_type="audio/wav"),
                "language": "wo",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Téléphone bi daanu, écran bi dafa tas.")
        self.assertEqual(post.call_args.args[0], "https://api.soynade.ai/v1/audio/transcriptions")
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer test-soynade-key")
        self.assertEqual(post.call_args.kwargs["data"]["language"], "wo")
        self.assertEqual(post.call_args.kwargs["data"]["temperature"], "0")
        self.assertEqual(post.call_args.kwargs["files"]["file"][0], "voix.wav")

    def test_audio_transcription_rejects_unsupported_file_type(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            "/api/ia/transcription/",
            {"audio": SimpleUploadedFile("voix.exe", b"audio", content_type="application/octet-stream")},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("audio", response.data)

    @patch.dict("os.environ", {"SOYNADE_API_KEY": "test-soynade-key"})
    @patch("diagnostics.services.requests.post")
    def test_empty_transcription_explains_how_to_record_voice(self, post):
        response_from_provider = Mock(status_code=200)
        response_from_provider.json.return_value = {"text": "  "}
        post.return_value = response_from_provider

        response = self.client.post(
            "/api/ia/transcription/",
            {"audio": SimpleUploadedFile("voix.wav", b"RIFFfake", content_type="audio/wav")},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("Soynade n’a reconnu aucune parole", response.data["detail"])

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
        self.assertEqual(
            post.call_args.kwargs["json"]["messages"][1]["content"],
            '{"appareil": "Téléphone", "marque": "", "description": "Le téléphone ne charge plus depuis hier.", "ville": "", "quartier": ""}',
        )

    def test_diagnostic_accepts_and_forwards_photo_to_vision_model(self):
        self.client.force_authenticate(self.user)
        image_buffer = BytesIO()
        Image.new("RGB", (2, 2), color="red").save(image_buffer, format="PNG")
        image_buffer.seek(0)
        photo = SimpleUploadedFile("panne.png", image_buffer.read(), content_type="image/png")
        resultat = {
            "categorie": "Électronique",
            "specialite": "Téléphonie",
            "probleme_probable": "Écran endommagé",
            "causes_possibles": [],
            "questions_a_poser": [],
            "niveau_urgence": "normal",
            "conseils_securite": [],
            "confiance": 0.8,
            "avertissement": "À confirmer par un réparateur.",
        }
        reponse_modele = Mock(status_code=200)
        reponse_modele.json.return_value = {"choices": [{"message": {"content": json.dumps(resultat)}}]}
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-token"}), patch(
            "diagnostics.services.requests.post", return_value=reponse_modele
        ) as post:
            response = self.client.post(
                self.url,
                {"description": "L’écran du téléphone est fissuré.", "photos": [photo]},
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contenu = post.call_args.kwargs["json"]["messages"][1]["content"]
        self.assertIsInstance(contenu, list)
        self.assertEqual(contenu[1]["type"], "image_url")
        self.assertTrue(contenu[1]["image_url"]["url"].startswith("data:image/png;base64,"))

    def test_prompt_includes_safety_warning_for_self_repair(self):
        prompt = DiagnosticIAService._prompt_system()

        self.assertIn("professionnel du diagnostic", prompt)
        self.assertIn("réparer", prompt)
        self.assertIn("vous-même", prompt)
        self.assertIn("wolof", prompt)
        self.assertIn("mélange des deux langues", prompt)
        self.assertIn("si la description est en wolof", prompt)
        self.assertIn("Réponds en wolof", prompt)

    @patch.dict("os.environ", {}, clear=True)
    def test_diagnostic_returns_service_unavailable_when_not_configured(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            self.url,
            {"description": "Le réfrigérateur ne refroidit plus."},
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch.dict("os.environ", {"SOYNADE_API_KEY": "test-soynade-key"})
    @patch("diagnostics.services.requests.post")
    def test_audio_transcription_explains_soynade_credit_limit(self, post):
        self.client.force_authenticate(self.user)
        provider_response = Mock(status_code=402, content=b"payment required")
        provider_response.json.return_value = {"detail": "Insufficient credits."}
        post.return_value = provider_response

        response = self.client.post(
            "/api/ia/transcription/",
            {"audio": SimpleUploadedFile("voix.wav", b"RIFFfake", content_type="audio/wav")},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("Insufficient credits", response.data["detail"])
