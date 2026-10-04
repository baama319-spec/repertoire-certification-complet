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
- configuration : HUGGINGFACE_API_TOKEN
- modèle optionnel : HUGGINGFACE_DIAGNOSTIC_MODEL

Copier .env.example vers .env, puis remplacer hf_votre_token_ici par un token
Hugging Face disposant de l'accès aux modèles Inference Providers. Redémarrer
Django après toute modification de .env.

Le modèle utilisé par défaut est meta-llama/Llama-3.1-8B-Instruct. La réponse est une
aide au diagnostic et doit être confirmée par un réparateur professionnel.

Notifications e-mail (n8n) :
- importer `n8n/repar-system-notification-workflow.json` dans n8n ;
- renseigner les identifiants Gmail sur le nœud **Envoyer email**, puis activer le workflow ;
- définir `N8N_NOTIFICATION_WEBHOOK_URL` dans `.env` et redémarrer Django.

Le backend envoie les données à l'URL de production `/webhook/...`. Pour tester
manuellement dans l'éditeur n8n, utiliser provisoirement `/webhook-test/...` pendant
que **Listen for test event** est activé.
