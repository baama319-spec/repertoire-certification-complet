# ReparSystem

Application Vue 3 / Vite pour mettre en relation des clients et des réparateurs.

## Démarrage

```bash
npm install
npm run dev
```

Pour utiliser l'API locale, démarrez aussi le backend dans `repar-system back` :

```bash
python manage.py runserver 8001
```

Le serveur Vite redirige alors `/api` et `/media` vers Django sur le port `8001`.

Le routage est centralisé dans `src/router/index.js`.
