# PLAN D'ACTIONS

Ce document détaille (et décrits les étapes d'implémentation) de certaines des taches présentes dans le fichier `TODO.md`.
Un regroupement par Sprints peut être envisagé dans ce document, selon le nombre de tâches à implémenter.
La priorisation des tâches est définie dans `TODO.md` et doit être respectée pour éviter de se disperser sur des points moins urgents.

## Contexte et Lignes Directrices (Héritées du plan de migration)

- **Séparation des rôles** : Garder une séparation claire entre l'outil applicatif (`UnityAssetsManager`) et le pipeline de curation (`_Helpers/04_Assets/AssetsCuration/`).
- **Nomenclature** : Le nom officiel est `UnityAssetsManager`. Toute ancienne référence (AssetManager, AssetManager V1, AssetsManager V2) est dépréciée.

**REGLE D'OR : Toujours proposer d'effectuer les corrections de bugs et les corrections immédiates en premier. Elles sont listées dans les section "Corrections immédiates" et "Bugs" du fichier `TODO.md`.**

Chaque fois qu'une modification est teminée:

- dans ce document:
  - ajouter "DONE " en début du titre de la section correspondante (ex: `### 1. [FIL1] Sections de filtres collapsables` devient `### 1. DONE [FIL1] Sections de filtres collapsables`)
  - les sections terminées sont régulièrement effacées de ce document pour ne conserver que les tâches en cours ou à venir
- dans `TODO.md`:
  - cocher la case associée
  - supprimer la tache de la liste des Groupes
  - déplacer la tache au début de la section "Terminés" à la fin du fichier (ex: `### Terminés`)

## Priorités de travail

### 0. DONE [BUG5] Exporter uniquement les assets filtrés

- Corriger l'endpoint `POST /api/export` pour réutiliser le `filter_stack` courant de l'interface.
- Conserver la compatibilite avec l'export par profil lorsque l'UI ne fournit pas de pile de filtres explicite.
- Verifier que les alias de colonnes restent appliques de la meme manière dans l'export simple et l'export batch.
- Ajouter une regression test sur l'export interactif pour garantir que les lignes exclues n'apparaissent plus.

### 1. [PROF1] Harmoniser les profils avec `column_aliases`

- Normaliser tous les profils JSONC afin qu'ils exposent `column_aliases` avec une structure homogène.
- Verifier les profils existants pour detecter les alias implicites encore deplaces dans des champs historiques.
- Ajouter des tests sur le chargement et l'usage des alias dans les filtres, les exports et les profils sauvegardes.

### 2. [PAG1/PAG2] Revoir la pagination et le nombre d'entrees visibles

- Ajouter une pagination dupliquee au-dessus du tableau, avec le texte de synthese complet.
- Deplacer le selecteur du nombre d'entrees par page a gauche de la zone de pagination.
- Verifier que les compteurs affiches en haut et en bas restent synchronises après tri, recherche et filtrage.

### 3. [AFF8/AFF9/AFF10] Recomposer l'affichage principal

- Rendre les sections `Controles` et `Donnees` repliables sans perdre l'etat courant.
- Ajouter un panneau `Message` juste sous le titre pour centraliser tous les retours d'information.
- Supprimer les doublons de messages entre le haut et le bas de page.
- Stabiliser le layout final en 5 blocs: Titre, Message, Contrôles, Données, Options.

### 4. [AFF6/AFF7/AFF5] Decomposer les contrôles en sous-sections lisibles

- Isoler la recherche dans un panneau `Recherche` avec le toggle regex sur la meme ligne.
- Isoler la selection des colonnes dans un panneau `Colonnes à afficher` avec un filtre rapide par nom.
- Remonter les options globales dans un panneau `Options` distinct.
- Deplacer l'option d'affichage des erreurs CSV et ajouter le filtre des assets invalides (FEAT4).
- Nettoyer les redondances visuelles entre les titres de panneaux et les titres internes.

### 5. [AFF10] Finaliser la hiérarchie de l'UI

- Faire converger le comportement des panneaux collapsables vers une hiérarchie stable et previsible.
- Replacer `Profil` dans `Filtrage` au lieu de l'ancienne popup dédiée.
- Regrouper les actions de filtrage, sauvegarde et export au meme endroit.
- Valider l'ordre de lecture visuel sur desktop et sur ecran reduit.

### 6. [REF4/REF2] Consolider les points techniques qui supportent l'UI

- Garder le logging centralise et lisible pendant les changements de layout et d'export.
- Limiter les regressions en isolant les ajustements de routes, de serialisation et d'etat front-end.
- Eviter tout nouveau couplage entre l'export, le filtrage et les anciennes branches legacy.

### 7. [API4/API3] Verrouiller le contrat d'API et les routes de support

- Revalider la coherence entre `app.py`, `lib/routes.py` et `openapi.yaml` apres les ajustements d'export.
- Maintenir la structure d'erreur uniforme sur les endpoints de support et de configuration.
- Ajouter ou ajuster les tests API si de nouveaux chemins de code apparaissent pendant la refonte de l'UI.

### 8. [DOC1/DOC2/DOC3] Garder la documentation synchronisee

- Mettre a jour `README.md`, `API_GUIDE.md` et `openapi.yaml` au fil des changements visibles.
- Conserver `SQLITE_SUPPORT.md` comme guide cible pour SQLite uniquement.
- Ajouter un court changelog fonctionnel pour chaque lot de modification importante.

### 9. [MIG1/MIG2/MIG3] Ne pas rouvrir les sujets de migration closes

- Laisser les routes legacy et les anciennes nomenclatures en etat stable tant qu'aucun besoin nouveau ne les touche.
- Surveiller les references residuelles dans les docs, tests et messages utilisateur.
- Ne rouvrir une migration que si elle est necessaire pour un besoin actif du backlog.

### 10. [CI1/CI2] Conserver la base de configuration et les scripts d'automatisation

- Verifier que les chemins de configuration et les scripts de versionnement restent coherents.
- Eviter toute modification qui casserait les exports automatises ou les profils utilises en headless.

### 11. STANDBY [FEAT2] Scraping direct depuis le Unity Store

- Ne pas engager cette feature tant que le cœur de l'application et les exports ne sont pas stabilises.
- Garder le sujet documenté pour une reprise ultérieure, avec la question du cache et de Cloudflare.

### 12. STANDBY [IDEA1] Filtrage avancé logique

- Reporter cette piste tant que les filtres existants, les profils et l'export ne sont pas parfaitement alignes.
- Conserver l'idée pour une phase dédiée si la demande remonte après stabilisation de l'UX courante.
