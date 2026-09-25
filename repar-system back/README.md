# ReparSystem Backend

API REST Django du projet ReparSystem.

Installation : créer un environnement virtuel, installer requirements.txt, puis lancer :
python manage.py migrate
python manage.py runserver

Les ressources CRUD sont sous /api/ : utilisateurs, clients, reparateurs,
specialites, localisations, demandes, realisations, avis et notifications.

Diagnostic IA texte :
- endpoint authentifié : POST /api/ia/diagnostic/
- configuration : HUGGINGFACE_API_TOKEN
- modèle optionnel : HUGGINGFACE_DIAGNOSTIC_MODEL

Copier .env.example vers .env, puis remplacer hf_votre_token_ici par un token
Hugging Face disposant de l'accès aux modèles Inference Providers. Redémarrer
Django après toute modification de .env.

Le modèle utilisé par défaut est meta-llama/Llama-3.1-8B-Instruct. La réponse est une
aide au diagnostic et doit être confirmée par un réparateur professionnel.
