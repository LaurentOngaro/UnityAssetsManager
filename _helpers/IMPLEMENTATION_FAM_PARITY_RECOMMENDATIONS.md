# Plan d'implémentation - recommandations FAM vers UAM

Objectif : capitaliser sur les optimisations observées dans `FabAssetsManager` pour améliorer la robustesse, la maintenabilité et la traçabilité de `UnityAssetsManager`.

## Portée

Ce plan couvre 3 axes principaux identifiés dans FAM et absents (ou simplifiés) dans UAM :

1. Centralisation et standardisation des erreurs API (`errors.py`).
2. Amélioration du système de logging (`RotatingFileHandler`).
3. Endpoints de diagnostic et de configuration à chaud.

## Détails d'implémentation

### REF3 - Gestion centralisée des erreurs API

But :

- Uniformiser les réponses d'erreur et simplifier le déclenchement d'erreurs partout dans le code.

Approche (Inspirée de FAM) :

- Créer un fichier `errors.py` contenant une Enum `ErrorCode` (ex: `INVALID_PAYLOAD`, `NOT_FOUND`, etc.) et une classe d'exception `AppError`.
- Remplacer l'actuelle fonction locale `api_error()` dans `routes.py` par l'utilisation de `create_error_response()` ou d'un `@app.errorhandler(AppError)` au niveau de Flask.
- Cela rendra le code plus lisible et le contrat API strictement prédictible.

### REF4 - Amélioration du système de logging

But :

- Permettre une traçabilité pérenne (surtout utile si UAM tourne en tâche de fond ou via des scripts headless).

Approche (Inspirée de FAM) :

- Remplacer l'actuel `logging.basicConfig(..., stream=sys.stdout)` par une configuration supportant un `RotatingFileHandler`.
- Ajouter des paramètres dans `config.json` (ou `app_settings.py`) : `log_level`, `log_output` (Console, File, Both), `log_max_bytes`, et `log_backup_count`.
- Écrire les logs dans un fichier `app.log` à la racine de UAM.

### API4 - Endpoints de diagnostic et configuration

But :

- Permettre à des scripts d'automatisation ou au frontend de vérifier facilement l'état du backend.

Approche (Inspirée de FAM) :

- Ajouter des routes `/api/test` (healthcheck basique) et `/api/config` (lecture/modification de la configuration de logging en temps réel).
- Facilite le débuggage en permettant de passer le serveur en mode `DEBUG` sans avoir à le redémarrer ou à modifier le fichier JSON manuellement.
