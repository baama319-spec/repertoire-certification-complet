import json
import logging
import os
import re
import tempfile

import requests
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class DiagnosticIAError(Exception):
    """Erreur contrôlée lors de l'appel ou du décodage du modèle IA."""


class TranscriptionIAError(Exception):
    """Erreur contrôlée lors de la transcription d'un enregistrement audio."""


class TraductionIAError(Exception):
    """Erreur contrôlée lors de la traduction d'une description de panne."""


class TraductionDiagnosticService:
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    default_model = "gemini-3.8-flash"

    def __init__(self, http_client=requests):
        self.http_client = http_client
        self.token = os.getenv("GEMINI_API_KEY", "")
        self.model = os.getenv("GEMINI_TRANSLATION_MODEL", self.default_model)

    def traduire(self, description):
        if not self.token:
            raise TraductionIAError("La traduction français-wolof n’est pas configurée.")

        try:
            response = self.http_client.post(
                self.endpoint.format(model=self.model),
                headers={"x-goog-api-key": self.token},
                json={
                    "contents": [{
                        "parts": [{
                            "text": (
                                "Traduis en français cette description de panne. Elle peut être en wolof, "
                                "en français ou mélanger les deux langues. Si elle est déjà en français, "
                                "restitue-la sans en changer le sens. Préserve les marques, modèles, "
                                "noms de pièces et symptômes; ne devine pas un terme wolof incertain, "
                                "signale-le brièvement entre crochets. Retourne uniquement le texte français, "
                                "sans introduction ni commentaire.\n\nDescription : "
                                f"{description}"
                            )
                        }]
                    }],
                    "generationConfig": {"temperature": 0, "maxOutputTokens": 1024},
                },
                timeout=45,
            )
        except requests.RequestException as error:
            logger.exception("Gemini translation request failed (%s)", type(error).__name__)
            raise TraductionIAError("Gemini est temporairement inaccessible pour traduire la description.") from error

        if response.status_code >= 400:
            messages = {
                400: "Gemini n’a pas pu traiter cette description. Vérifiez le texte et le modèle configuré.",
                401: "La clé Gemini est invalide. Vérifiez GEMINI_API_KEY dans le fichier .env.",
                403: "La clé Gemini n’a pas accès au modèle de traduction.",
                404: "Le modèle Gemini de traduction est introuvable. Vérifiez GEMINI_TRANSLATION_MODEL.",
                429: "Le quota ou la limite de requêtes Gemini est atteint. Vérifiez les quotas Google AI Studio ou réessayez plus tard.",
            }
            raise TraductionIAError(messages.get(
                response.status_code,
                f"Gemini ne peut pas traduire la description (erreur HTTP {response.status_code}).",
            ))

        try:
            traduction = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise TraductionIAError("La réponse de traduction Gemini est invalide.") from error

        traduction = " ".join(str(traduction).split())
        if not traduction:
            raise TraductionIAError("Gemini n’a pas renvoyé de traduction. Vous pouvez modifier la description et réessayer.")
        return traduction


class TranscriptionAudioService:
    default_model = "gemini-3.5-transcribe"

    def __init__(self, http_client=requests):
        self.http_client = http_client
        self.token = os.getenv("GEMINI_API_KEY", "")
        self.model = os.getenv("GEMINI_TRANSCRIPTION_MODEL", self.default_model)

    def transcrire(self, fichier):
        if not self.token:
            raise TranscriptionIAError("La transcription vocale n'est pas configurée.")

        client = genai.Client(
            api_key=self.token,
            http_options=types.HttpOptions(timeout=180_000),
        )
        fichier_gemini = None
        try:
            extension = os.path.splitext(fichier.name)[1] or ".webm"
            with tempfile.NamedTemporaryFile(suffix=extension) as fichier_temporaire:
                for morceau in fichier.chunks():
                    fichier_temporaire.write(morceau)
                fichier_temporaire.flush()
                fichier_gemini = client.files.upload(file=fichier_temporaire.name)

            interaction = client.interactions.create(
                model=self.model,
                input=[{
                    "type": "audio",
                    "uri": fichier_gemini.uri,
                    "mime_type": fichier_gemini.mime_type or fichier.content_type or "audio/webm",
                }],
                generation_config={
                    "transcription_config": {
                        "language_codes": [],
                        "mode": "smart",
                    }
                },
                store=False,
            )
            texte = interaction.output_text
        except Exception as error:
            logger.exception("Gemini transcription failed (%s)", type(error).__name__)
            status_code = getattr(error, "code", None)
            messages = {
                401: "La clé Gemini est invalide. Vérifiez GEMINI_API_KEY dans le fichier .env.",
                403: "La clé Gemini n’a pas accès au modèle de transcription.",
                404: "Le modèle Gemini de transcription est introuvable. Vérifiez GEMINI_TRANSCRIPTION_MODEL.",
                429: "Le quota ou la limite de requêtes Gemini est atteint. Vérifiez Google AI Studio.",
            }
            raise TranscriptionIAError(messages.get(
                status_code,
                "La transcription Gemini a échoué. Consultez le journal Django pour le détail, puis réessayez.",
            )) from error
        finally:
            if fichier_gemini is not None:
                try:
                    client.files.delete(name=fichier_gemini.name)
                except Exception:
                    logger.warning("Could not delete temporary Gemini audio file", exc_info=True)

        texte = " ".join(str(texte or "").split())
        if not texte:
            raise TranscriptionIAError("Aucune parole n'a été détectée. Vous pouvez saisir le texte manuellement.")
        return texte


class DiagnosticIAService:
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
    default_model = "google/gemini-2.5-flash"

    def __init__(self, http_client=requests):
        self.http_client = http_client
        self.token = os.getenv("OPENROUTER_API_KEY", "")
        self.model = os.getenv("OPENROUTER_DIAGNOSTIC_MODEL", self.default_model)

    def analyser(self, donnees):
        if not self.token:
            raise DiagnosticIAError("Le service de diagnostic IA n'est pas configuré.")

        try:
            response = self.http_client.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:5173"),
                    "X-Title": "ReparSystem",
                },
                json={
                    "model": self.model,
                    "provider": {"sort": "latency"},
                    "messages": [
                        {"role": "system", "content": self._prompt_system()},
                        {"role": "user", "content": self._prompt_utilisateur(donnees)},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 700,
                },
                timeout=45,
            )
        except requests.RequestException as error:
            raise DiagnosticIAError("Le fournisseur IA est temporairement indisponible.") from error
        if response.status_code >= 400:
            messages = {
                400: "OpenRouter a refusé la requête. Vérifiez le modèle configuré.",
                401: "La clé OpenRouter est invalide ou expirée. Vérifiez OPENROUTER_API_KEY et redémarrez le backend.",
                403: "OpenRouter refuse l’accès au modèle ou au fournisseur sélectionné. Vérifiez les autorisations de la clé.",
                404: "Le modèle configuré est introuvable sur OpenRouter. Vérifiez OPENROUTER_DIAGNOSTIC_MODEL.",
                402: "OpenRouter indique que le compte n’a pas assez de crédits. Ajoutez des crédits dans le compte OpenRouter.",
                429: "La limite de requêtes OpenRouter est atteinte. Vérifiez le quota ou réessayez plus tard.",
            }
            message = messages.get(
                response.status_code,
                f"OpenRouter est indisponible (erreur HTTP {response.status_code}). Réessayez plus tard.",
            )
            raise DiagnosticIAError(message)

        try:
            contenu = response.json()["choices"][0]["message"]["content"]
            return self._decoder_json(contenu)
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise DiagnosticIAError("La réponse du modèle IA est invalide.") from error

    @staticmethod
    def _prompt_system():
        return """Tu es l'assistant de pré-diagnostic de ReparSystem.
Comprends les descriptions de pannes en français, en wolof et dans un mélange des deux langues, y compris les formulations orales et les noms locaux de symptômes ou de pièces. Interprète le sens sans pénaliser les fautes de transcription. Ne traduis pas arbitrairement un terme wolof incertain : pose une question de clarification dans la langue principalement utilisée lorsque c'est nécessaire. Réponds dans cette même langue autant que possible.
Tu ne dois jamais présenter une hypothèse comme une certitude et tu dois recommander un réparateur pour toute intervention technique.
Si la description mentionne fumée, odeur de brûlé, étincelles, fuite de gaz, batterie gonflée ou danger électrique, mets niveau_urgence à \"urgent\" et conseille d'arrêter et débrancher l'appareil si cela est possible sans danger.
Dans le champ avertissement, ajoute toujours un rappel de sécurité explicite : ne pas essayer de réparer l'appareil ou le chargeur vous-même si vous n'êtes pas un professionnel du diagnostic. Demande de contacter un réparateur qualifié et de ne pas manipuler les composants électroniques sous tension.
Réponds uniquement avec un objet JSON valide, sans Markdown, possédant exactement ces clés:
 categorie, specialite, probleme_probable, causes_possibles, questions_a_poser, niveau_urgence, conseils_securite, confiance, avertissement.
causes_possibles, questions_a_poser et conseils_securite sont des tableaux de chaînes.
confiance est un nombre entre 0 et 1.
Utilise \"inconnu\" lorsque les informations ne permettent pas de conclure."""

    @staticmethod
    def _prompt_utilisateur(donnees):
        return json.dumps(
            {
                "appareil": donnees.get("appareil", ""),
                "marque": donnees.get("marque", ""),
                "description": donnees["description"],
                "ville": donnees.get("ville", ""),
                "quartier": donnees.get("quartier", ""),
            },
            ensure_ascii=False,
        )

    @staticmethod
    def _decoder_json(contenu):
        contenu = contenu.strip()
        bloc = re.search(r"```(?:json)?\s*(.*?)\s*```", contenu, re.DOTALL)
        if bloc:
            contenu = bloc.group(1)
        resultat = json.loads(contenu)
        if not isinstance(resultat, dict):
            raise ValueError("Le diagnostic n'est pas un objet JSON.")
        champs_requis = {
            "categorie",
            "specialite",
            "probleme_probable",
            "causes_possibles",
            "questions_a_poser",
            "niveau_urgence",
            "conseils_securite",
            "confiance",
            "avertissement",
        }
        if set(resultat) != champs_requis:
            raise ValueError("Le diagnostic ne respecte pas le contrat attendu.")
        if not all(isinstance(resultat[champ], list) for champ in ("causes_possibles", "questions_a_poser", "conseils_securite")):
            raise ValueError("Les listes du diagnostic sont invalides.")
        if not isinstance(resultat["confiance"], (int, float)) or not 0 <= resultat["confiance"] <= 1:
            raise ValueError("La confiance du diagnostic est invalide.")
        return resultat
