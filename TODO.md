# TODOs

## Bugs (last: BUG1)

## Corrections immédiates (last:CI1)

## Améliorations du projet

Pour plus de détails sur l'implémentation de ces modifications, consulter le fichier `_helpers\PLAN_ACTIONS.md` qui détaille les étapes à suivre pour chaque tâche.

### Priorités d'implémentation

classement des demandes par priorité de la plus urgente à la moins urgente:

- REF3 (Centralisation erreurs API)
- REF4 (Amélioration du logging)
- API4 (Endpoints de diagnostic)
- AFF1 (Redimensionner les colonnes)
- AFF2 (Popup détail de ligne)
- MIG2 (Déprécier les flux legacy)
- MIG3 (Archiver V1 après validation)
- INT1 (Service de normalisation raw multi-boutiques)
- INT2 (Provider Unity)
- INT3 (Provider Fab)
- INT4 (Provider boutiques manuelles)

### Documentation (last: DOC3)

### Filtrage (last: )

### Pagination (last: )

### Affichage (last: AFF2)

- [ ] AFF1: pouvoir Redimensionner les colonnes (au mieux par drag-and-drop sinon via un menu de configuration de l'affichage)
- [ ] AFF2: Popup détail ligne ( manque d'info, qu'est ce que cela signifie ?)

### Features (last: FEAT1)

### Renforcement du contrat API (last: API4)

- [ ] API4: Ajouter des endpoints de diagnostic et de configuration (ex: `/api/test`, `/api/config`) pour faciliter l'automatisation.

### Refactoring (last: REF4)

- [ ] REF3: Centraliser la gestion des erreurs API via un module `errors.py` (classes et Enum), sur le modèle de FAM.
- [ ] REF4: Améliorer le système de logging avec un `RotatingFileHandler` et des paramètres dynamiques (niveau, sortie).

### Migration (last: MIG3)

- [ ] MIG2: Finaliser la dépréciation des flux legacy `assetsCuration/85X_A00_*.json` après migration complète.
- [ ] MIG3: Archiver V1 (`AssetsManager/assetManager.py`) après validation de la chaîne complète V2.

### Intégration future (last: INT4) - utilité à questionner

- [ ] INT1: Intégrer le moteur `buildStoreRawNormalized` comme service dans UnityAssetsManager.
- [ ] INT2: Ajouter provider Unity (SQLite prioritaire, CSV fallback) pour produire `raw_assets_normalized.json`.
- [ ] INT3: Ajouter provider Fab à partir des exports/cache consolidés (sans rapatrier FabAssetsManager).
- [ ] INT4: Ajouter provider boutiques manuelles via `raw_assets.md`.

### Idées à creuser (last: IDEA1) - utilité à questionner

- [ ] Filtres avancés (date ranges, etc)
- [ ] Import depuis URL

## Terminés

- [x] API1: Vérifier la cohérence entre implémentation Flask et `openapi.yaml`.
- [x] API2: Ajouter des tests API pour les cas d'erreurs standards.
- [x] API3: Finaliser le contrat d'erreur uniforme sur toutes les routes.
- [x] DOC1: Analyse et priorisation des docs de migration terminées. `plan_action_UnityAssetsManager.md` archivé et fusionné avec `PLAN_ACTIONS.md`.
- [x] DOC2: Consolider les redondances entre `README.md`, `API_GUIDE.md` et docs techniques.
- [x] DOC3: Garder `SQLITE_SUPPORT.md` orienté setup SQLite uniquement.
- [x] MIG1: Mettre à jour prompts/docs restants vers la nomenclature `UnityAssetsManager`.
- [x] REF2: Modulariser l'application (découper le monolithe `app.py` en modules distincts, supprimer les dépendances legacy, optimiser SQLite). Voir [REFACTORING_MODULARIZATION.md](./_helpers/REFACTORING_MODULARIZATION.md).
- [x] CI1: déplacer `config.json` en `config/config.json`
- [x] CI2: Initialiser des dépôts Git locaux dédiés pour UnityAssetsManager et FabAssetsManager (commit initial effectué).
- [x] Implémenter `/api/batch-export` pour usage headless/automation.
- [x] Ajouter mode include/exclude explicite dans le filter builder.
- [x] Ajouter tests de non-régression sur export templates (md/csv/json/txt).
- [x] Ajouter une checklist manuelle scriptée (include/exclude + save/load profil).
- [x] Ajouter un versionning ciblé sur fichiers applicatifs importants (version source + bump script).
