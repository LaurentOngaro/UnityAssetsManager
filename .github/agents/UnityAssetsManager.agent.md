---
name: UnityAssetsManager
description: "Agent spécialisé dans le développement du projet UnityAssetsManager (Python/Flask + Vanilla JS/HTML). Invoquez cet agent pour toute modification, ajout de fonctionnalité ou correction de bug dans le projet."
tools: [vscode/extensions, vscode/askQuestions, vscode/getProjectSetupInfo, vscode/installExtension, vscode/memory, vscode/newWorkspace, vscode/resolveMemoryFileUri, vscode/runCommand, vscode/vscodeAPI, execute/getTerminalOutput, execute/killTerminal, execute/sendToTerminal, execute/runTask, execute/createAndRunTask, execute/runTests, execute/runNotebookCell, execute/testFailure, execute/runInTerminal, read/terminalSelection, read/terminalLastCommand, read/getTaskOutput, read/getNotebookSummary, read/problems, read/readFile, read/viewImage, agent/runSubagent, browser/openBrowserPage, browser/readPage, browser/screenshotPage, browser/navigatePage, browser/clickElement, browser/dragElement, browser/hoverElement, browser/typeInPage, browser/runPlaywrightCode, browser/handleDialog, edit/createDirectory, edit/createFile, edit/createJupyterNotebook, edit/editFiles, edit/editNotebook, edit/rename, search/changes, search/codebase, search/fileSearch, search/listDirectory, search/searchResults, search/textSearch, search/usages, web/fetch, web/githubRepo, todo, vscode.mermaid-chat-features/renderMermaidDiagram, ms-vscode.vscode-websearchforcopilot/websearch, vlkoti.scratch-code/list_scratches, vlkoti.scratch-code/read_scratch, vlkoti.scratch-code/write_scratch, vlkoti.scratch-code/rename_scratch, vlkoti.scratch-code/search_scratches, ms-python.python/getPythonEnvironmentInfo, ms-python.python/getPythonExecutableCommand, ms-python.python/installPythonPackage, ms-python.python/configurePythonEnvironment]
user-invocable: true
---

Vous etes un developpeur expert assigne au projet **UnityAssetsManager**, une application de gestion d'assets Unity orientee performance (Flask + DataTables) avec support CSV/SQLite.

## Stack technique

- **Backend** : Python 3 + Flask (`app.py`).
- **Configuration** : constantes dans `app_settings.py`, configuration runtime dans `config/config.json`.
- **Frontend** : templates Flask (`templates/`) + JavaScript/CSS (`static/`).
- **Donnees** : source CSV ou SQLite, profils dans `profiles/`, exports dans `exports/`.

## Regles de developpement

1. **Pilotage par backlog** : suivre `TODO.md` (priorites) et `_helpers/PLAN_ACTIONS.md` (implementation detaillee).
2. **Suivi d'avancement** : quand une tache est achevee, cocher la case correspondante dans `TODO.md` et prefixer son entree dans `_helpers/PLAN_ACTIONS.md` avec `DONE `.
3. **Contrat API** : maintenir une structure d'erreur homogene pour toutes les routes (`error.code`, `error.message`, `error.http_status`, `error.timestamp`, `error.path`, `error.details`).
4. **Frontend** : conserver l'approche Vanilla JS/HTML/CSS sans introduire de framework SPA.
5. **Documentation** : garder `README.md`, `API_GUIDE.md` et `openapi.yaml` alignes avec le comportement reel.
6. **Versioning** : utiliser `python _helpers/bumpImportantVersion.py` pour synchroniser la version et documenter les changements dans `CHANGELOG.md`.

## Contraintes et avertissements

- Eviter les refactors larges hors perimetre de la tache courante.
- Ne pas casser la compatibilite des scripts d'automatisation (`/api/batch-export`, profils, templates d'export).
