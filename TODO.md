# TODOs

## Bugs (last: BUG1)

## Corrections immédiates (last:CI2)

- [ ] CI1: déplacer `config.json` en `config/config.json`
- [x] CI2: créer des modules git dédiés pour les 2 projets (car ils appartiennes à 2 dépot différents)

## Améliorations du projet

Pour plus de détails sur l'implémentation de ces modifications, consulter le fichier `_helpers\PLAN_ACTIONS.md` qui détaille les étapes à suivre pour chaque tâche.

### Priorités d'implémentation

classement des demandes par priorité de la plus urgente à la moins urgente:

- GE2 (Création agent & instructions type FabAssetsManager)
- CI1 (Déplacer config.json vers config/config.json)
- REF1 (Isoler constantes et variables globales)
- REF2 (Découpage de app.py en modules)
- API3 (Standardiser le format des erreurs API pendant le découpage des routes)
- DOC1 (Fusionner les documents de suivi et migration)
- DOC2 (Consolider README et API_GUIDE)
- API1 (Cohérence OpenAPI)
- API2 (Tests d'API)
- GE1 (Actions de maintenance UI)
- DOC3 (Update SQLITE_SUPPORT)
- AFF1 (Drag-and-drop colonnes)
- AFF2 (Popup détail de ligne)
- FEAT1 (Parité V1 restante)
- MIG1 (Nomenclature globale)

### Documentation (last: DOC3)

- [ ] DOC1: Analyse et prioriser ou Fusionner les docs "MIGRATION STATE V1 to V2" "plan_action_UnityAssetsManager" "PLAN_ACTIONS"
- [ ] DOC2: Consolider les redondances entre `README.md`, `API_GUIDE.md` et docs techniques.
- [ ] DOC3: Garder `SQLITE_SUPPORT.md` orienté setup SQLite uniquement.

### filtrage (last: )

### pagination (last: )

### gestion (last: GE1)

- [ ] GE1: ajouter une zone avec des action de maintenance en bas de la colonne de gauche
- [ ] GE2: créer des instructions et un agent spécifique à ce projet
  - reprendre ce qui a été fait pour `FabAssetsManager` et l'adapter à `UnityAssetsManager` (voir le dossier "H:\Sync\Scripts\Python\03_apps\FabAssetsManager\.github" pour les exemples d'agents et d'instructions)

### refactoring (last: REF2)

- [ ] REF1: Déplacer les constantes de configuration et magic numbers (ex: `DATA_PATH`, `DEFAULT_EXPORT_TEMPLATES`) codés en dur dans `app.py` vers le fichier de configuration dédié ou un module `config.py`. (Nécessite de générer un doc de validation temporaire avant d'appliquer).
- [ ] REF2: Modulariser l'application (découper le monolithe `app.py` en modules distincts, supprimer les dépendances legacy, optimiser SQLite). Voir `_helpers/REFACTORING_MODULARIZATION.md`.

### Affichage (last: AFF2)

- [ ] AFF1 - pouvoir Redimensionner les colonnes (au mieux par drag-and-drop sinon via un menu de configuration de l'affichage)
- [ ] AFF2 - Popup détail ligne ( manque d'info, qu'est ce que cela signifie ?)

### Features (last: FEAT1)

- [ ] FEAT1: traiter `MIGRATION STATE V1 to V2 .md` comme backlog de parité V1 restant.

### Renforcement du contrat API (last: API4)

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

- [x] CI2: Initialiser des dépôts Git locaux dédiés pour UnityAssetsManager et FabAssetsManager (commit initial effectué).
- [x] Implémenter `/api/batch-export` pour usage headless/automation.
- [x] Ajouter mode include/exclude explicite dans le filter builder.
- [x] Ajouter tests de non-régression sur export templates (md/csv/json/txt).
- [x] Ajouter une checklist manuelle scriptée (include/exclude + save/load profil).
- [x] Ajouter un versionning ciblé sur fichiers applicatifs importants (version source + bump script).
