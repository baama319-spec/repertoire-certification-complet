import json
import os
import re

import requests


class DiagnosticIAError(Exception):
    """Erreur contrôlée lors de l'appel ou du décodage du modèle IA."""


class DiagnosticIAService:
    endpoint = "https://router.huggingface.co/v1/chat/completions"
    default_model = "meta-llama/Llama-3.1-8B-Instruct"

    def __init__(self, http_client=requests):
        self.http_client = http_client
        self.token = os.getenv("HUGGINGFACE_API_TOKEN", "")
        self.model = os.getenv("HUGGINGFACE_DIAGNOSTIC_MODEL", self.default_model)

    def analyser(self, donnees):
        if not self.token:
            raise DiagnosticIAError("Le service de diagnostic IA n'est pas configuré.")

        try:
            response = self.http_client.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
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
            raise DiagnosticIAError("Le fournisseur IA a refusé la demande.")

        try:
            contenu = response.json()["choices"][0]["message"]["content"]
            return self._decoder_json(contenu)
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise DiagnosticIAError("La réponse du modèle IA est invalide.") from error

    @staticmethod
    def _prompt_system():
        return """Tu es l'assistant de pré-diagnostic de ReparSystem.
Analyse les pannes d'appareils et équipements décrites en français.
Tu ne dois jamais présenter une hypothèse comme une certitude et tu dois recommander un réparateur pour toute intervention technique.
Si la description mentionne fumée, odeur de brûlé, étincelles, fuite de gaz, batterie gonflée ou danger électrique, mets niveau_urgence à \"urgent\" et conseille d'arrêter et débrancher l'appareil si cela est possible sans danger.
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
