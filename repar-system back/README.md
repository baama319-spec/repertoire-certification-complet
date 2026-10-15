# ReparSystem Backend

API REST Django du projet ReparSystem.

Installation : créer un environnement virtuel, installer requirements.txt, puis lancer :
python manage.py migrate
python manage.py runserver

Les ressources CRUD sont sous /api/ : utilisateurs, clients, reparateurs,
specialites, localisations, demandes, realisations, avis et notifications.

## Passer de SQLite à PostgreSQL en conservant les données

Le backend utilise SQLite par défaut dans une nouvelle installation. Pour le PostgreSQL
local fourni, installer les dépendances (`pip install -r requirements.txt`), configurer
le `.env` local (ne jamais versionner ses identifiants), puis démarrer le conteneur :

```env
DB_ENGINE=postgresql
DB_NAME=reparsystem
DB_USER=reparsystem
DB_PASSWORD=mot-de-passe-local
DB_HOST=127.0.0.1
DB_PORT=5433
DB_CONN_MAX_AGE=60
```

Le fichier `docker-compose.postgres.yml` crée une base PostgreSQL 16 persistante sur
`127.0.0.1:5433` (ce port évite de toucher à un PostgreSQL déjà présent sur `5432`) :

```sh
docker compose --env-file .env -f docker-compose.postgres.yml up -d
```

Avant le transfert, arrêter le serveur et sauvegarder `db.sqlite3` ainsi que le dossier
`medias/`. Exporter les données à partir de SQLite avant de passer `DB_ENGINE` à
`postgresql` :

```sh
python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --indent 2 > /tmp/reparsystem-sqlite-data.json
```

Appliquer d'abord les migrations sur PostgreSQL, puis importer le fichier exporté :

```sh
python manage.py migrate
python manage.py loaddata /tmp/reparsystem-sqlite-data.json
python manage.py sqlsequencereset utilisateurs reparateurs clients demandes specialites localisations realisations avis notifications authtoken | docker exec -i reparsystem-postgres psql -U reparsystem -d reparsystem
python manage.py check
```

Contrôler ensuite les utilisateurs, clients, réparateurs, demandes, avis et les médias
avant de remettre le service en production. Garder la sauvegarde SQLite intacte tant que
le contrôle n'est pas terminé. Les fichiers téléversés ne sont pas inclus dans le JSON :
ils restent dans `medias/`, à copier séparément si le déploiement change de serveur.

Diagnostic IA texte :
- endpoint authentifié : POST /api/ia/diagnostic/
- fournisseur : OpenRouter
- configuration : OPENROUTER_API_KEY
- modèle optionnel : OPENROUTER_DIAGNOSTIC_MODEL (par défaut : google/gemini-2.5-flash)

Saisie vocale du diagnostic :
- endpoint authentifié : POST /api/ia/transcription/ (multipart, champ `audio`, maximum 20 Mo)
- fournisseur de transcription : OpenAI Audio Transcriptions, modèle `whisper-1` par défaut
- configuration : `OPENAI_API_KEY` ; modèle optionnel : `OPENAI_TRANSCRIPTION_MODEL`
- la détection automatique permet de transcrire le français, le wolof et leur mélange ; le texte reste modifiable avant le diagnostic
- l'audio est transmis au fournisseur pour transcription et n'est pas conservé par l'application

Copier .env.example vers .env, puis remplacer la valeur d'exemple par une clé
créée dans le compte OpenRouter. Garder cette clé secrète et ne jamais la committer.
Le routage sélectionne le fournisseur disponible avec la plus faible latence.
OpenRouter peut exiger des crédits selon le modèle et le fournisseur. Redémarrer
Django après toute modification de .env.

Le modèle utilisé par défaut est google/gemini-2.5-flash. La réponse est une
aide au diagnostic et doit être confirmée par un réparateur professionnel.
La clé OpenAI est distincte de la clé OpenRouter. Garder les deux clés secrètes,
ne jamais les exposer dans le frontend et redémarrer Django après leur configuration.

Notifications e-mail (n8n) :
- importer `n8n/repar-system-notification-workflow.json` dans n8n ;
- renseigner les identifiants Gmail sur le nœud **Envoyer email**, puis activer le workflow ;
- définir `N8N_NOTIFICATION_WEBHOOK_URL` dans `.env` et redémarrer Django.

Le backend envoie les données à l'URL de production `/webhook/...`. Pour tester
manuellement dans l'éditeur n8n, utiliser provisoirement `/webhook-test/...` pendant
que **Listen for test event** est activé.
