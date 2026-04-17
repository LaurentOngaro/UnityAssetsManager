# TODOs

## Bugs (last: BUG2)

- [ ] BUG2: valeur undefined dans le texte en bas de page: "UnityAssetsManager Flask • undefined / 5059 lignes affichées

## Corrections immédiates (last:CI1)

## Améliorations du projet

Pour plus de détails sur l'implémentation de ces modifications, consulter le fichier `_helpers\PLAN_ACTIONS.md` qui détaille les étapes à suivre pour chaque tâche (si besoin).

### Priorités d'implémentation

classement des demandes par priorité de la plus urgente à la moins urgente:

### Documentation (last: DOC3)

### Filtrage (last: )

### Pagination (last: )

### Affichage (last: AFF4)

- [ ] AFF4: mémoriser la dimension des colonnes et la rétablir à l'ouverture suivante

### Features (last: FEAT2)

- [ ] FEAT2:  faire du scrapping direct depuis le unity store

### Renforcement du contrat API (last: API4)

### Refactoring (last: REF4)

### API (last: API4)

### Migration (last: MIG3)

- [ ] MIG3: Archiver V1 (`AssetsManager/assetManager.py`) après validation de la chaîne complète V2.

### Intégration future (last: INT2)

- [ ] INT2: Finaliser l'export batch pour générer les 29 fichiers de catégories bruts (profils) dans `assetsExports/Unity/`.

### Idées à creuser (last: IDEA1) - utilité à questionner

- [ ] IDEA1: Ajouter un mode de filtrage avancé avec des opérateurs logiques (AND/OR) et des plages de valeurs (ex: date range).

### Décision actée Hors Périmètre (Pivot stratégique - UAM reste spécialisé Unity)

- [x] INT1: NE PAS intégrer le moteur `buildStoreRawNormalized`. (Uniformisation gérée par les scripts du pipeline de curation).
- [x] INT3: NE PAS intégrer de provider Fab. (Géré par FAM - FabAssetsManager).
- [x] INT4: NE PAS intégrer de provider boutiques manuelles. (Géré par `buildStoreRawNormalized.py`).

## Terminés

- [x] MIG2: Finaliser la dépréciation des flux legacy `assetsCuration/85X_A00_*.json` après migration complète.
- [x] AFF3: Reprendre le theme de couleur "sombre" de FabAssetsManager"
- [x] AFF1: pouvoir Redimensionner les colonnes (au mieux par drag-and-drop sinon via un menu de configuration de l'affichage)
- [x] AFF2: Popup détail ligne ( manque d'info, qu'est ce que cela signifie ?)
- [x] API4: Ajouter des endpoints de diagnostic et de configuration (ex: `/api/test`, `/api/config`) pour faciliter l'automatisation.
- [x] REF4: Améliorer le système de logging avec un `RotatingFileHandler` et des paramètres dynamiques (niveau, sortie).
- [x] REF3: Centraliser la gestion des erreurs API via un module `errors.py` (classes et Enum), sur le modèle de FAM.
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
