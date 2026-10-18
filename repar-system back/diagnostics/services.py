import base64
import json
import io
import logging
import os
import re

import requests

logger = logging.getLogger(__name__)


class DiagnosticIAError(Exception):
    """Erreur contrôlée lors de l'appel ou du décodage du modèle IA."""


class TranscriptionIAError(Exception):
    """Erreur contrôlée lors de la transcription d'un enregistrement audio."""


class TraductionIAError(Exception):
    """Erreur contrôlée lors de la traduction d'une description de panne."""


class VoixIAError(Exception):
    """Erreur contrôlée lors de la génération d'une réponse audio."""


class VoixAssistantService:
    endpoint = "https://api.soynade.ai/v1/text-to-speech"

    def __init__(self, http_client=requests):
        self.http_client = http_client
        self.token = os.getenv("SOYNADE_API_KEY", "")

    def generer(self, texte, language="fr"):
        texte = str(texte or "").strip()
        if not texte:
            raise VoixIAError("Le texte à lire est vide.")
        if not self.token:
            raise VoixIAError("La synthèse Soynade n’est pas configurée. Ajoutez SOYNADE_API_KEY dans le .env du backend.")
        try:
            response = self.http_client.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "text": texte,
                    "language": language if language in {"fr", "wo"} else "fr",
                    "output_format": "mp3",
                    "exaggeration": 0.2,
                    "temperature": 0.1,
                    "cfg_weight": 0.5,
                    "seed": 0,
                },
                timeout=90,
            )
        except requests.RequestException as error:
            logger.exception("Soynade TTS request failed (%s)", type(error).__name__)
            raise VoixIAError("Soynade est temporairement inaccessible pour générer la voix.") from error
        if response.status_code >= 400:
            raise VoixIAError(self._message_erreur(response))
        if not response.content:
            raise VoixIAError("Soynade n’a pas renvoyé de contenu audio.")
        return response.content

    @staticmethod
    def _message_erreur(response):
        try:
            payload = response.json()
            detail = payload.get("detail", payload.get("message", payload.get("error", "")))
            if isinstance(detail, dict):
                detail = detail.get("message", "")
            if isinstance(detail, str) and detail.strip():
                return f"Soynade : {detail.strip()[:300]}"
        except (ValueError, AttributeError):
            pass
        if response.status_code in {401, 403}:
            return "La clé Soynade est invalide ou n’a pas accès à cette API. Vérifiez SOYNADE_API_KEY."
        if response.status_code == 402:
            return "Le solde de crédits Soynade est insuffisant. Vérifiez la facturation de votre espace de travail."
        if response.status_code == 429:
            return "La limite de requêtes Soynade est atteinte. Réessayez plus tard."
        return f"Soynade a refusé la génération audio (HTTP {response.status_code})."


class TraductionDiagnosticService:
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    default_model = "gemini-3.6-flash"

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
    endpoint = "https://api.soynade.ai/v1/audio/transcriptions"

    def __init__(self, http_client=requests):
        self.http_client = http_client
        self.token = os.getenv("SOYNADE_API_KEY", "")

    def transcrire(self, fichier, language="auto"):
        if not self.token:
            raise TranscriptionIAError("La transcription Soynade n’est pas configurée. Ajoutez SOYNADE_API_KEY dans le .env du backend.")
        fichier.seek(0)
        contenu = fichier.read()
        fichier.seek(0)
        if not contenu:
            raise TranscriptionIAError("L’enregistrement reçu est vide. Vérifiez le microphone puis réessayez.")
        type_audio = getattr(fichier, "content_type", "") or "audio/wav"
        extension = os.path.splitext(fichier.name)[1].lower()
        if extension not in {".wav", ".mp3", ".flac"}:
            raise TranscriptionIAError("Format audio non pris en charge : Soynade attend un fichier WAV, MP3 ou FLAC.")
        donnees = {"response_format": "json", "temperature": "0"}
        if language in {"fr", "wo", "en"}:
            donnees["language"] = language
        try:
            response = self.http_client.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.token}"},
                data=donnees,
                files={"file": (fichier.name, io.BytesIO(contenu), type_audio)},
                timeout=120,
            )
        except requests.RequestException as error:
            logger.exception("Soynade transcription request failed (%s)", type(error).__name__)
            raise TranscriptionIAError("Soynade est temporairement inaccessible pour transcrire l’audio.") from error
        if response.status_code >= 400:
            raise TranscriptionIAError(VoixAssistantService._message_erreur(response))
        try:
            texte = response.json().get("text", "")
        except (ValueError, AttributeError) as error:
            raise TranscriptionIAError("Soynade a renvoyé une réponse de transcription invalide.") from error

        texte = " ".join(str(texte or "").split())
        if not texte:
            raise TranscriptionIAError(
                "Soynade n’a reconnu aucune parole claire. Vérifiez le microphone, parlez après le démarrage, "
                "puis gardez le micro actif jusqu’à la fin de votre phrase avant de l’arrêter."
            )
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
                        {"role": "user", "content": self._contenu_utilisateur(donnees)},
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
Comprends les descriptions de pannes en français, en wolof et dans un mélange des deux langues, y compris les formulations orales et les noms locaux de symptômes ou de pièces. Interprète le sens sans pénaliser les fautes de transcription. Ne traduis pas arbitrairement un terme wolof incertain : pose une question de clarification dans la langue principalement utilisée lorsque c'est nécessaire.
Analyse aussi les photos jointes si elles sont présentes : décris uniquement les indices visuels clairement observables, utilise-les comme complément au texte et ne déduis pas une panne certaine à partir d’une image seule.
Règle de langue : si la description est en wolof, réponds en wolof dans le texte de la réponse et dans les questions et conseils, sauf si tu dois maintenir un terme technique en français. Si la description est en français, réponds en français. Si la description est mixte, réponds dans la langue principale utilisée par le message, en conservant les termes techniques utiles.
Tu ne dois jamais présenter une hypothèse comme une certitude et tu dois recommander un réparateur pour toute intervention technique.
Si la description mentionne fumée, odeur de brûlé, étincelles, fuite de gaz, batterie gonflée ou danger électrique, mets niveau_urgence à \"urgent\" et conseille d'arrêter et débrancher l'appareil si cela est possible sans danger.
Dans le champ avertissement, ajoute toujours un rappel de sécurité explicite : ne pas essayer de réparer l'appareil ou le chargeur vous-même si vous n'êtes pas un professionnel du diagnostic. Demande de contacter un réparateur qualifié et de ne pas manipuler les composants électroniques sous tension.
Réponds uniquement avec un objet JSON valide, sans Markdown, possédant exactement ces clés:
 categorie, specialite, probleme_probable, causes_possibles, questions_a_poser, niveau_urgence, conseils_securite, confiance, avertissement.
causes_possibles, questions_a_poser et conseils_securite sont des tableaux de chaînes.
confiance est un nombre entre 0 et 1.
Utilise \"inconnu\" lorsque les informations ne permettent pas de conclure.
Réponds en wolof si la description est en wolof, ou en français si la description est en français."""

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
    def _contenu_utilisateur(donnees):
        contenu = [{"type": "text", "text": DiagnosticIAService._prompt_utilisateur(donnees)}]
        for photo in donnees.get("photos", []):
            photo.seek(0)
            image = base64.b64encode(photo.read()).decode("ascii")
            photo.seek(0)
            mime_type = getattr(photo, "content_type", None) or "image/jpeg"
            contenu.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{image}"},
            })
        return contenu if len(contenu) > 1 else contenu[0]["text"]

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


class AssistantConversationService:
    endpoint = DiagnosticIAService.endpoint
    default_model = DiagnosticIAService.default_model

    def __init__(self, http_client=requests):
        self.http_client = http_client
        self.token = os.getenv("OPENROUTER_API_KEY", "")
        self.model = os.getenv("OPENROUTER_DIAGNOSTIC_MODEL", self.default_model)

    def repondre(self, messages, language="auto", photos=None):
        if not self.token:
            raise DiagnosticIAError("Le service d’assistance IA n’est pas configuré.")

        contenu = [{"role": message["role"], "content": message["content"].strip()} for message in messages]
        if photos:
            dernier_message = contenu[-1]
            dernier_message["content"] = [{"type": "text", "text": dernier_message["content"]}]
            for photo in photos:
                photo.seek(0)
                image = base64.b64encode(photo.read()).decode("ascii")
                photo.seek(0)
                mime_type = getattr(photo, "content_type", None) or "image/jpeg"
                dernier_message["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{image}"},
                })

        try:
            response = self.http_client.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:5173"),
                    "X-Title": "ReparSystem - Assistant",
                },
                json={
                    "model": self.model,
                    "provider": {"sort": "latency"},
                    "messages": [
                        {"role": "system", "content": self._prompt_system(language)},
                        *contenu,
                    ],
                    "temperature": 0.4,
                    "max_tokens": 220,
                },
                timeout=45,
            )
        except requests.RequestException as error:
            logger.exception("OpenRouter assistant request failed (%s)", type(error).__name__)
            raise DiagnosticIAError("Le service d’assistance est temporairement indisponible.") from error

        if response.status_code >= 400:
            messages_erreur = {
                401: "La clé OpenRouter est invalide. Vérifiez OPENROUTER_API_KEY dans le fichier .env.",
                402: "Le compte OpenRouter n’a pas assez de crédits pour répondre.",
                429: "La limite de requêtes IA est atteinte. Réessayez un peu plus tard.",
            }
            raise DiagnosticIAError(messages_erreur.get(
                response.status_code,
                f"Le service IA est indisponible (erreur HTTP {response.status_code}).",
            ))

        try:
            texte = response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise DiagnosticIAError("La réponse de l’assistant est invalide.") from error

        texte = " ".join(str(texte or "").split())
        if not texte:
            raise DiagnosticIAError("L’assistant n’a pas renvoyé de réponse. Réessayez.")
        return texte

    @staticmethod
    def _prompt_system(language):
        consigne_langue = {
            "fr": "Réponds toujours en français.",
            "wo": "Réponds toujours en wolof (langue du Sénégal), avec un wolof simple et naturel.",
            "auto": "Détecte la langue de l’utilisateur et réponds dans cette langue : français, wolof ou leur mélange.",
        }[language]
        return (
            "Tu es l’assistant de ReparSystem, un service sénégalais qui aide à trouver des réparateurs. "
            "Aide à comprendre les pannes d’appareils et à préparer une demande de réparation. "
            "Réponses très courtes : 1 à 3 phrases, environ 40 mots maximum. "
            "Avance étape par étape : propose une seule vérification simple et sans danger à la fois, puis demande le résultat avant de continuer. "
            "Ne donne jamais une longue liste de causes, de questions ou de vérifications. "
            "Si plusieurs vérifications sont utiles, choisis la plus simple et attends la réponse de l’utilisateur. "
            "Ne répète pas le même message dans deux langues. Si l’utilisateur demande explicitement un guide complet, donne au plus 2 petites étapes par réponse. "
            "Pose au maximum une question courte si un détail manque. Une photo peut aider à décrire des indices visibles, "
            "mais ne permet jamais de confirmer une panne. Ne prétends jamais qu’un diagnostic est certain. "
            "Pour fumée, étincelles, odeur de brûlé, batterie gonflée, fuite ou risque électrique, recommande "
            "d’arrêter l’appareil et de le débrancher uniquement si cela ne présente aucun danger, puis de contacter "
            "un professionnel. Ne donne pas d’instructions pour manipuler des composants sous tension ni pour "
            "effectuer une réparation risquée. Ne demande aucune donnée bancaire, mot de passe ou code secret. "
            f"{consigne_langue} Reste chaleureux, clair et concis."
        )
