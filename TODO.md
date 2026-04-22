# TODOs

## Bugs (last: BUG5)

## Corrections immédiates (last:CI1)

## Améliorations du projet

Pour plus de détails sur l'implémentation de ces modifications, consulter le fichier `_helpers\PLAN_ACTIONS.md` qui détaille les étapes à suivre pour chaque tâche (si besoin).

### Priorités d'implémentation

classement des demandes par priorité de la plus urgente à la moins urgente:

### Documentation (last: DOC3)

### Filtrage et profils (last: PROF1)

### Pagination (last: PAG1)

### Affichage (last: AFF10)

- [ ] AFF11: dans la zone "colonnes à afficher":
  - diminuer la largeur de la liste et afficher à droite une zone contenant les boutons suivants:
    - "Afficher tous" :affiche tous les champs disponibles dans la source de données
    - "Afficher profil" :affiche uniquement les champs définis dans le champs "column_profile" du profil actif
    - "Afficher minimum" :RAZ la selection et conserve uniquement displayname et url (ou slug si url indisponible)
    - "Inverser" :inverse la selection
- [ ] AFF12: dans la zone "Profils":
  - [ ] diminuer la taille des 2 zones de texte et mettre tous les boutons sur la droite, le tout sur une ligne (au lieu de 2 actuellement)
- [ ] AFF13: améliorer le design général
  - apliquer un theme et un design cohérent
  - enlever les icones dans les titre des sous sections (ex: "Recherche", "Colonnes à afficher", "Profils") pour alléger le design
  - uniformiser la taille et le design des boutons car quasiement TOUS les boutons sont différents(sauf cas particulier tel que supprimer que reste en rouge)

#### part 1: réorganisation de l'UI: ajouter de la cohérence, de la lisibilité et permettre de reduire les sections pour se concentrer sur l'essentiel

### Features (last: FEAT4)

- [ ] FEAT2:  faire du scrapping direct depuis le unity store

### Renforcement du contrat API (last: API4)

### Refactoring (last: REF4)

### API (last: API4)

### Migration (last: MIG3)

### Intégration future (last: INT4)

- [ ] INT4: Traduire l'application en Anglais pour faciliter l'internationalisation future et l'adoption par des utilisateurs non francophones.

### Idées à creuser (last: IDEA1) - utilité à questionner

- [ ] IDEA1: Ajouter un mode de filtrage avancé avec des opérateurs logiques (AND/OR) et des plages de valeurs (ex: date range).

## Terminés

- [x] PAG2: deplacer le selecteur du nombre d'assets par page (ex "Afficher 50 entrées") à gauche de la zone de pagination (cad à gauche du texte "Affichage de 1 à 50 sur 5 898 entrées")
- [x] PAG1: mettre un doublon de la zone de pagination en haut de la liste (incluant le texte "Affichage de 1 à 50 sur 5 898 entrées" )
- [x] AFF8: rendre les zone "Controles" et "Données" collapsable
- [x] AFF9: ajoute un panel collapsable (similaire à "Contrôles"), nommé "Message"
- [x] AFF6: mettre la zone de recherche dans un panel collapsable (similaire à "Générateur de filtres", inside "Contrôles"), nommé "Recherche", placer l'option RegExe et la recherche sur la meme ligne
- [x] AFF7: mettre les  Colonnes à afficher dans un panel collapsable  (similaire à "Générateur de filtres", inside "Contrôles"), nommé "Colonnes à afficher"
- [x] AFF5: ajoute un panel collapsable (similaire à "Générateur de filtres"), nommé "Options" qui recevra les options du l'app (même niveau que "Contrôles")
- [x] AFF10: layout de présentation final
- [x] BUG5: supprimer les caractères "spéciaux" dans le nom des assets tel que ("・")
- [x] FEAT4: ajoute une option "filter les assets invalides" pour filter les assets (quelque soit le profil), à qui il manque le slug+url ou les champs d'affichage requis; appliqué sur export interactif si coché et toujours actif en batch export
- [x] PROF1: ajouter les "column_aliases" dans tous les profils json
- [x] BUG5: les assets exportés ne sont pas filtrés (tous les asset sont présents dans les exports, même ceux qui sont filtrés dans l'app)
- [x] AFF4: mémoriser la dimension des colonnes et la rétablir à l'ouverture suivante
- [x] BUG4: lorsque qu'un profil est chargé, l'application du filtre échoue silencieusement et la liste n'est pas filtrée (route api_data ignorait filter_stack)
- [x] FEAT3: ajouter une gestion des alias de colonnes (par ex: "URL" et "AssetLink" peuvent être utilisés indépendamment, principalement dans les template d'export ou bien dans les filtres)
- [x] BUG3: un clic sur le tri de colonne ne change pas la liste
- [x] BUG2: valeur undefined dans le texte en bas de page: "UnityAssetsManager Flask • undefined / 5059 lignes affichées
- Décision actée (Pivot stratégique): UAM reste spécialisé Unity donc pas d'intégration des autres boutiques (un script dédié gérera l'uniformisation des données):
  - [-] INT1: ignoré, NE PAS intégrer le moteur `buildStoreRawNormalized`. (Uniformisation gérée par les scripts du pipeline de curation).
  - [-] INT3: ignoré, NE PAS intégrer de provider Fab. (Géré par FAM - FabAssetsManager).
  - [-] INT4: ignoré, NE PAS intégrer de provider boutiques manuelles. (Géré par `buildStoreRawNormalized.py`).
- [x] INT2: Finaliser l'export batch pour générer les fichiers de catégories bruts (profils) dans `assetsExports/Unity/`.
- [x] MIG3: Archiver V1 (`AssetsManager/assetManager.py`) après validation de la chaîne complète V2.
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
