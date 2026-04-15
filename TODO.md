# TODOs

## Bugs (last: BUG1)

## Corrections immédiates (last:CI1)

## Améliorations du projet

Pour plus de détails sur l'implémentation de ces modifications, consulter le fichier `_helpers\PLAN_ACTIONS.md` qui détaille les étapes à suivre pour chaque tâche.

### Priorités d'implémentation

classement simplifie des demandes par priorité de la plus urgente à la moins urgente, avec les mêmes identifiants que `PLAN_ACTIONS.md`:

- REF2 (Découper `app.py` en modules et optimiser SQLite)
- API3 (Uniformiser le contrat d'erreur sur toutes les routes)
- API1 (Vérifier la cohérence OpenAPI)
- API2 (Ajouter des tests API d'erreurs standards)
- DOC1 (Fusionner les documents de suivi et migration)
- DOC2 (Consolider `README.md` et `API_GUIDE.md`)
- DOC3 (Garder `SQLITE_SUPPORT.md` orienté setup SQLite)
- AFF1 (Redimensionner les colonnes)
- AFF2 (Popup détail de ligne)
- FEAT1 (Parité V1 restante)
- MIG1 (Mettre à jour la nomenclature)
- MIG2 (Déprécier les flux legacy)
- MIG3 (Archiver V1 après validation)
- INT1 (Service de normalisation raw multi-boutiques)
- INT2 (Provider Unity)
- INT3 (Provider Fab)
- INT4 (Provider boutiques manuelles)

### Documentation (last: DOC3)

- [ ] DOC1: Analyse et prioriser ou Fusionner les docs "MIGRATION STATE V1 to V2" ([source backlog](./_helpers/MIGRATION%20STATE%20V1%20to%20V2%20.md)), [plan_action_UnityAssetsManager](./_helpers/plan_action_UnityAssetsManager.md) et [PLAN_ACTIONS](./_helpers/PLAN_ACTIONS.md).
- [ ] DOC2: Consolider les redondances entre `README.md` ([README](./README.md)), `API_GUIDE.md` ([API guide](./API_GUIDE.md)) et docs techniques.
- [ ] DOC3: Garder `SQLITE_SUPPORT.md` ([support SQLite](./_helpers/SQLITE_SUPPORT.md)) orienté setup SQLite uniquement.

### filtrage (last: )

### pagination (last: )

- [ ] REF2: Modulariser l'application (découper le monolithe `app.py` en modules distincts, supprimer les dépendances legacy, optimiser SQLite). Voir [REFACTORING_MODULARIZATION.md](./_helpers/REFACTORING_MODULARIZATION.md).

### Affichage (last: AFF2)

- [ ] AFF1 - pouvoir Redimensionner les colonnes (au mieux par drag-and-drop sinon via un menu de configuration de l'affichage)
- [ ] AFF2 - Popup détail ligne ( manque d'info, qu'est ce que cela signifie ?)

### Features (last: FEAT1)

- [ ] FEAT1: traiter `MIGRATION STATE V1 to V2 .md` ([backlog migration](./_helpers/MIGRATION%20STATE%20V1%20to%20V2%20.md)) comme backlog de parité V1 restant.

### Renforcement du contrat API (last: API3)

- [ ] API1: Vérifier la cohérence entre implémentation Flask et `openapi.yaml`.
- [ ] API2: Ajouter des tests API pour les cas d'erreurs standards (payload invalide, profil absent, setup invalide).
- [ ] API3: Finaliser le contrat d'erreur uniforme sur toutes les routes (`error.code`, `error.message`, `error.http_status`, `error.timestamp`, `error.path`, `error.details`).
  - reprendre ce qui a été fait pour `FabAssetsManager` et l'adapter à `UnityAssetsManager`.

### migration (last: MIG3)

- [ ] MIG1: Mettre à jour prompts/docs restants vers la nomenclature `UnityAssetsManager`.
- [ ] MIG2: Finaliser la dépréciation des flux legacy `assetsCuration/85X_A00_*.json` après migration complète.
- [ ] MIG3: Archiver V1 (`AssetsManager/assetManager.py`) après validation de la chaîne complète V2.

### Intégration future (last: INT4) - utilité à questionner

- [ ] INT1: Intégrer le moteur `buildStoreRawNormalized` comme service dans UnityAssetsManager.
- [ ] INT2: Ajouter provider Unity (SQLite prioritaire, CSV fallback) pour produire `raw_assets_normalized.json`.
- [ ] INT3: Ajouter provider Fab à partir des exports/cache consolidés (sans rapatrier FabAssetsManager).
- [ ] INT4: Ajouter provider boutiques manuelles via `raw_assets.md`.

### idées à creuser (last: IDEA1) - utilité à questionner

- [ ] Filtres avancés (date ranges, etc)
- [ ] Import depuis URL

## Terminés

- [x] CI1: déplacer `config.json` en `config/config.json`
- [x] CI2: Initialiser des dépôts Git locaux dédiés pour UnityAssetsManager et FabAssetsManager (commit initial effectué).
- [x] Implémenter `/api/batch-export` pour usage headless/automation.
- [x] Ajouter mode include/exclude explicite dans le filter builder.
- [x] Ajouter tests de non-régression sur export templates (md/csv/json/txt).
- [x] Ajouter une checklist manuelle scriptée (include/exclude + save/load profil).
- [x] Ajouter un versionning ciblé sur fichiers applicatifs importants (version source + bump script).
