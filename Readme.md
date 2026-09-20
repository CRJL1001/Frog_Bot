## Dépendance

Installer ffmpeg : https://ffmpeg.org/download.html -> pour le module de sons aléatoires

Voir les bibliothèques python dans requirments.txt

## PostgreSQL

Les rappels sont stockés dans PostgreSQL via Docker Compose. Ajoutez au fichier `.env` :

```env
DB_PASSWORD=un_mot_de_passe
```

Puis démarrez les services avec :

```bash
docker compose up -d --build
```

Au premier démarrage, les rappels présents dans `reminders.json` sont importés une seule fois dans PostgreSQL.
