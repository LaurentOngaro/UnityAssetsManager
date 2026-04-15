// ============================================================================
// UnityAssetsManager - static/js/app.js
// ============================================================================
// Description: Logique client (Vanilla JS) pour l'interface DataTables.
// Version: 1.2.3
// ============================================================================

// Configuration
const MIN_COL_WIDTH = 150;  // Largeur minimum en pixels pour chaque colonne

let dataTable;
let currentColumns = [];
let currentFilterColumns = [];
let currentFilterStack = [];
let currentAliasMap = {};
let currentProfileName = null; // Nom du profil actif
let exportModal, profileModal;
let loadedTemplates = []; // Templates d'export chargés depuis le serveur

// ============================================================================
// GESTION DES TEMPLATES D'EXPORT
// ============================================================================

function loadExportTemplates() {
    console.log('[Templates] Récupération des templates d\'export...');

    $.ajax({
        url: '/api/templates',
        type: 'GET',
        success: function(resp) {
            const templates = resp.templates || [];
            loadedTemplates = templates; // Stocker pour usage ultérieur
            console.log('[Templates] ' + templates.length + ' templates chargés');

            // Vider et repeupler le select
            const $select = $('#exportTemplate');
            $select.empty();

            if (templates.length === 0) {
                $select.append('<option value="">Aucun template disponible</option>');
                return;
            }

            templates.forEach(function(tmpl) {
                $select.append(`<option value="${tmpl.name}" data-desc="${tmpl.description}">${tmpl.name}</option>`);
            });

            // Afficher la description du premier template par défaut
            if (templates.length > 0) {
                $('#exportTemplateDesc').text(templates[0].description);
            }

            // Listener pour afficher la description quand on change de template
            $select.off('change').on('change', function() {
                const selectedOption = $(this).find('option:selected');
                const desc = selectedOption.data('desc') || '';
                $('#exportTemplateDesc').text(desc);
                updateExportPreview(); // Mettre à jour l'aperçu aussi
            });
        },
        error: function(xhr, status, err) {
            console.error('[Templates] Erreur chargement:', err);
            $('#exportTemplate').append('<option value="">❌ Erreur chargement templates</option>');
        }
    });
}

$(document).ready(function() {
    console.log('[UnityAssetsManager] Initialisation...');

    // --- debug configuration checkbox ---
    $('#chkParserWarnings').prop('checked', SHOW_PARSER_WARNINGS === true || SHOW_PARSER_WARNINGS === 'true');
    $('#chkParserWarnings').on('change', function() {
        const enabled = $(this).prop('checked');
        console.log('[Config] show_parser_warnings ->', enabled);
        $.ajax({
            url: '/api/config',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ show_parser_warnings: enabled }),
            success: function(resp) {
                showAlert('Paramètre sauvegardé', 'success');
            },
            error: function(xhr, status, err) {
                console.error('[Config] erreur sauvegarde', err);
                showAlert('Impossible de sauvegarder la configuration', 'danger');
            }
        });
    });

    exportModal = new bootstrap.Modal(document.getElementById('exportModal'));
    profileModal = new bootstrap.Modal(document.getElementById('profileModal'));

    initializeTable();
    setupEventHandlers();
    loadExportTemplates();  // Charger les templates d'export au démarrage
    updateDataInfo();
    loadProfilesList();  // Charger la liste des profils au démarrage
});

function initializeTable() {
    console.log('[Table] Initialisation DataTables...');

    // Récupérer les colonnes depuis le header
    currentColumns = $('#assetsTable thead th').map(function() {
        return $(this).text();
    }).get();

    // remplir le sélecteur de colonnes filtrables (utilisé dans UI des filtres)
    const opts = currentColumns.map(c => `<option value="${c}">${c}</option>`).join('');
    $('#filterColumnsSelector').html(opts);
    // restaurer sélection si profile chargé
    if (currentFilterColumns && currentFilterColumns.length) {
        $('#filterColumnsSelector').val(currentFilterColumns);
    }

    // Créer les définitions de colonnes pour DataTables (format objet)
    const columnDefs = currentColumns.map(function(colName) {
        return {
            data: colName,
            title: colName,
            width: MIN_COL_WIDTH + 'px',  // Largeur minimum pour chaque colonne
            render: function(data, type, row) {
                if (type === 'display' && data && data.length > 100) {
                    return '<span title="' + escapeHtml(data) + '">' +
                           escapeHtml(data.substring(0, 100)) + '...</span>';
                }
                return escapeHtml(data);
            }
        };
    });

    dataTable = $('#assetsTable').DataTable({
        processing: true,
        serverSide: true,
        searching: false,  // Utiliser notre propre champ de recherche
        paging: true,
        pageLength: 50,
        lengthMenu: [25, 50, 100, 250],
        order: [],
        columns: columnDefs,

        ajax: {
            url: '/api/data',
            type: 'GET',
            data: function(d) {
                // injecte la recherche globale directement dans l'objet structuré
                const searchVal = $('#searchInput').val() || '';
                const isRegex = $('#chkSearchRegex').prop('checked');
                d.search = d.search || {};
                d.search.value = searchVal;
                d.search.regex = isRegex;

                // Ajout debug pour vérifier ce qui part réellement
                console.log('[Ajax.data] envoi params', d);

                // filtres de profil ou créés manuellement
                if (currentFilterColumns && currentFilterColumns.length) {
                    d.filter_columns = JSON.stringify(currentFilterColumns);
                }
                if (currentFilterStack && currentFilterStack.length) {
                    d.filter_stack = JSON.stringify(currentFilterStack);
                }
                if (currentAliasMap && Object.keys(currentAliasMap).length) {
                    d.alias_map = JSON.stringify(currentAliasMap);
                }
                return d;
            },
            error: function(xhr, status, error) {
                console.error('[API] Erreur:', error, xhr.responseText);
                showAlert('Erreur lors du chargement des données', 'danger');
            }
        },


        language: {
            "url": "//cdn.datatables.net/plug-ins/1.13.7/i18n/fr-FR.json"
        },

        initComplete: function() {
            console.log('[Table] Prête à l\'affichage');
        }
    });
}

// ============================================================================
// GESTION DES ÉVÉNEMENTS
// ============================================================================

// Fonction globale pour recherche (accessible depuis n'importe où)
function performSearch() {
    const searchVal = $('#searchInput').val();
    const isRegex = $('#chkSearchRegex').prop('checked');
    console.log('[Search] Exécution recherche:', { searchVal, isRegex });
    if (!dataTable) {
        console.error('[Search] DataTable non initialisée!');
        return;
    }
    console.log('[Search] Lancement reload DataTable avec search:', searchVal);
    dataTable.ajax.reload(null, false);  // false = ne pas réinitialiser pagination
    console.log('[Search] Reload lancé');
}

function setupEventHandlers() {
    console.log('[Events] Configuration des handlers...');

    // Recherche avec bouton ou touche Entrée
    console.log('[Events] Attachement handlers recherche...');
    $('#btnSearch').on('click', function(e) {
        console.log('[Search] Click bouton détecté');
        performSearch();
    });
    $('#searchInput').on('keypress', function(e) {
        if (e.key === 'Enter') {
            console.log('[Search] Enter key détecté');
            performSearch();
        }
    });

    // Sélection des colonnes - Utiliser la visibilité native de DataTables
    $('#columnSelector').on('change', function() {
        console.log('[Columns] Changement des colonnes');
        const selectedCols = $(this).val() || [];

        // Cacher/montrer les colonnes selon la sélection
        dataTable.columns().every(function() {
            const colName = this.header().textContent;
            const shouldShow = selectedCols.length === 0 || selectedCols.includes(colName);
            this.visible(shouldShow);
        });

        updateDataInfo();
    });

    // Boutons
    $('#btnExport').on('click', showExportModal);
    $('#btnProfile').on('click', showProfileModal);
    $('#btnReset').on('click', resetFilters);
    $('#btnConfirmExport').on('click', performExport);
    $('#btnSaveProfile').on('click', saveProfile);
    $('#btnLoadProfile').on('click', loadProfile);
    $('#btnDeleteProfile').on('click', deleteProfile);

    // Sélection colonne filtrrable: analyser et afficher UI appropriée (textarea ou checkboxes)
    $('#filterBuilderCol').on('change', function() {
        const column = $(this).val();
        console.log('[FilterBuilder] Colonne sélectionnée:', column);

        if (!column) {
            // Reset UI
            $('#filterBuilderValue').show().val('');
            $('#filterBuilderCheckboxes').hide().empty();
            $('#filterBuilderValues').hide().empty();
            return;
        }

        // Analyser les valeurs uniques de la colonne pour détecter booléens
        analyzeColumnForBooleans(column, function(isBool, values) {
            if (isBool) {
                console.log('[FilterBuilder] Colonne booléenne detectée:', column, values);
                renderBooleanCheckboxes(column);
            } else {
                console.log('[FilterBuilder] Colonne texte/nombre:', column);
                // P3.4: Afficher dropdown des valeurs uniques
                loadColumnValues(column);
            }
        });
    });

    // P3.4: Recharger les valeurs si le toggle change
    $('#chkFilterDisplayedOnly').on('change', function() {
        const column = $('#filterBuilderCol').val();
        if (column) {
            loadColumnValues(column);
        }
    });

    $('#btnApplyFilters').on('click', function() {
        try {
            const parsed = JSON.parse($('#filterStackEditor').val() || '[]');
            currentFilterStack = Array.isArray(parsed) ? parsed : [];
            console.log('[Filter] stack appliquée:', currentFilterStack);
            renderFilterList();
            dataTable.ajax.reload();
            showAlert('Filtres appliqués', 'success');
        } catch (e) {
            console.error('[Filter] JSON invalide', e);
            showAlert('Format de filtres invalide (JSON)', 'danger');
        }
    });

    // Filter Builder handlers
    $('#btnAddFilter').on('click', function() {
        addFilterFromBuilder();
    });

    $('#btnClearAllFilters').on('click', function() {
        if (confirm('Vider tous les filtres ?')) {
            currentFilterStack = [];
            $('#filterStackEditor').val('[]');
            $('#filterBuilderCol').val('');
            $('#filterBuilderValue').val('');
            $('#filterBuilderCheckboxes').empty().hide();
            renderFilterList();
            dataTable.ajax.reload();
            console.log('[Filter] Tous les filtres supprimés');
        }
    });

    // Navigation
    $('#navReload').on('click', function(e) {
        e.preventDefault();
        reloadData();
    });

    $('#navStats').on('click', function(e) {
        e.preventDefault();
        showStats();
    });

    // Profile selector
    $('#profilesList').on('change', function() {
        if ($(this).val()) {
            $('#profileActions').show();
        } else {
            $('#profileActions').hide();
        }
    });

    // Export template preview
    $('#exportTemplate').on('change', updateExportPreview);
}

// ============================================================================
// EXPORT
// ============================================================================

function showExportModal() {
    console.log('[Export] Ouverture modal export');

    // Récupérer le vrai comptage filtré depuis le serveur (reflète tous les filtres appliqués)
    const searchVal = $('#searchInput').val() || '';
    const payload = {
        start: 0,
        length: 0, // On ne veut pas de data, juste le count
        'draw': 1,
        'search[value]': searchVal
    };

    // Ajouter filter_stack si présent
    if (currentFilterStack && currentFilterStack.length > 0) {
        payload.filter_stack = JSON.stringify(currentFilterStack);
        payload.alias_map = JSON.stringify(currentAliasMap || {});
    }

    if (currentFilterColumns && currentFilterColumns.length > 0) {
        payload.filter_columns = JSON.stringify(currentFilterColumns);
    }

    console.log('[Export] Demande comptage avec payload:', payload);

    $.ajax({
        url: '/api/data',
        type: 'GET',
        data: payload,
        success: function(resp) {
            const filteredCount = resp.recordsFiltered !== undefined ? resp.recordsFiltered : 0;
            console.log('[Export] Comptage réel filtré reçu:', filteredCount);
            $('#exportLineCount').text(filteredCount);
            updateExportPreview();
            exportModal.show();
        },
        error: function(xhr, status, err) {
            console.error('[Export] Erreur comptage API:', err, xhr.responseText);
            // Fallback: utiliser DataTables count si l'API échoue
            const info = dataTable.page.info();
            const filteredCount = info ? info.recordsFiltered : 0;
            $('#exportLineCount').text(filteredCount);
            updateExportPreview();
            exportModal.show();
        }
    });
}

function updateExportPreview() {
    const templateName = $('#exportTemplate').val();
    const cols = getVisibleColumns();

    // Chercher le template dans les templates chargés
    const template = loadedTemplates.find(t => t.name === templateName);

    // Aperçu basé sur le template réel
    let preview = `Format: ${templateName}\n`;

    if (template && template.description) {
        preview += `Description: ${template.description}\n`;
    }

    preview += `Colonnes: ${cols.slice(0, 3).join(', ')}${cols.length > 3 ? '...' : ''}\n`;
    preview += `---\n\n`;

    // Afficher un aperçu basé sur le pattern du template
    if (template && template.pattern) {
        const pattern = template.pattern;

        // Extraire les noms de colonnes du pattern
        const columnMatches = pattern.match(/%([^%]+)%/g);
        const usedColumns = columnMatches ? columnMatches.map(m => m.replace(/%/g, '')) : [];

        // Générer l'en-tête selon le format
        let headerLines = [];

        // Markdown table : format avec pipes
        if (pattern.includes('|') && !pattern.includes('{')) {
            const header = '| ' + usedColumns.join(' | ') + ' |';
            const separator = '|' + usedColumns.map(() => '---').join('|') + '|';
            headerLines = [header, separator];
        }
        // CSV : en-tête simple avec virgules
        else if (pattern.includes(',') && !pattern.includes('[') && !pattern.includes('(')) {
            headerLines = [usedColumns.join(',')];
        }
        // Markdown liste : commentaire HTML
        else if (pattern.trim().startsWith('-') || pattern.trim().startsWith('*')) {
            headerLines = [`<!-- Colonnes: ${usedColumns.join(', ')} -->`];
        }
        // Texte simple : commentaire
        else {
            headerLines = [`# Colonnes: ${usedColumns.join(', ')}`];
        }

        // Remplacer quelques placeholders par des exemples
        let exampleLine = pattern;
        exampleLine = exampleLine.replace(/%DisplayName%/g, 'Asset Name');
        exampleLine = exampleLine.replace(/%DisplayPublisher%/g, 'Publisher');
        exampleLine = exampleLine.replace(/%Version%/g, '1.0');
        exampleLine = exampleLine.replace(/%Url%/g, 'https://example.com');
        exampleLine = exampleLine.replace(/%DisplayCategory%/g, 'Category');
        exampleLine = exampleLine.replace(/%PackageTags%/g, 'tag1, tag2');
        exampleLine = exampleLine.replace(/%AssetRating%/g, '4.5');
        exampleLine = exampleLine.replace(/%PackageSource%/g, 'AssetStore');
        exampleLine = exampleLine.replace(/%Slug%/g, 'asset-slug');
        // Supprimer les autres placeholders non remplacés
        exampleLine = exampleLine.replace(/%[^%]+%/g, 'value');

        // Assembler aperçu : en-tête + exemples
        preview += `Exemple:\n`;
        if (headerLines.length > 0) {
            preview += headerLines.join('\n') + '\n';
        }
        preview += `${exampleLine}\n${exampleLine.replace('Asset Name', 'Another Asset')}\n...`;
    } else {
        // Fallback vers ancien système
        if (templateName && templateName.toLowerCase().includes('json')) {
            preview += `{\n  "assets": [\n    { "col1": "val1", "col2": "val2" },\n    ...\n  ]\n}`;
        } else if (templateName && templateName.toLowerCase().includes('markdown')) {
            preview += `| ${cols.slice(0, 3).join(' | ')} |\n`;
            preview += `|${Array(Math.min(cols.length, 3)).fill('---------').join('|')}|\n`;
            preview += `| val1 | val2 | val3 |`;
        } else {
            preview += `${cols.slice(0, 3).join(',')}\n`;
            preview += `val1,val2,val3\nval4,val5,val6\n...`;
        }
        preview += `val1,val2,...\nval3,val4,...`;
    }

    $('#exportPreviewText').text(preview);
}

function performExport() {
    console.log('[Export] Lancement export...');

    const template = $('#exportTemplate').val();
    const cols = getVisibleColumns();
    const searchValue = $('#searchInput').val();

    $.ajax({
        url: '/api/export',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            template: template,
            columns: cols,
            search: searchValue,
            filter_columns: currentFilterColumns,
            filter_stack: currentFilterStack,
            alias_map: currentAliasMap
        }),
        xhrFields: {
            responseType: 'blob'
        },
        success: function(blob) {
            console.log('[Export] Succès, téléchargement...');

            // Déterminer l'extension en fonction du template
            let ext = 'txt'; // Par défaut

            // Chercher le template dans les templates chargés
            const templateObj = loadedTemplates.find(t => t.name === template);

            if (templateObj && templateObj.pattern) {
                const pattern = templateObj.pattern.toLowerCase();
                const templateName = template.toLowerCase();

                // 1. Vérifier d'abord le nom explicite du template
                if (templateName.includes('json')) {
                    ext = 'json';
                }
                else if (templateName.includes('markdown') || templateName.includes('liste') || templateName.includes('table')) {
                    ext = 'md';
                }
                else if (templateName.includes('csv')) {
                    ext = 'csv';
                }
                // 2. Si pas trouvé, analyser le pattern
                else {
                    // Markdown table : contient des pipes
                    if (pattern.includes('|') && !pattern.includes('{')) {
                        ext = 'md';
                    }
                    // Markdown liste : commence par - ou *
                    else if (pattern.trim().startsWith('-') || pattern.trim().startsWith('*')) {
                        ext = 'md';
                    }
                    // CSV : séparateur virgule (mais pas dans URL ou syntaxe markdown)
                    else if (pattern.includes(',') && !pattern.includes('[') && !pattern.includes('(')) {
                        ext = 'csv';
                    }
                    // JSON : structure objet/array (pas syntaxe markdown)
                    else if ((pattern.includes('{') || pattern.includes('[')) && !pattern.includes('](')) {
                        ext = 'json';
                    }
                }
            } else {
                // Fallback: heuristiques basées sur le nom
                if (template.toLowerCase().includes('json')) {
                    ext = 'json';
                } else if (template.toLowerCase().includes('markdown')) {
                    ext = 'md';
                } else if (template.toLowerCase().includes('csv')) {
                    ext = 'csv';
                }
            }

            // Nom du fichier: profil actif ou valeur par défaut
            const baseName = currentProfileName ? currentProfileName : 'assets_export';
            const filename = `${baseName}_${new Date().toISOString().slice(0, 10)}.${ext}`;

            // Trigger download
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            window.URL.revokeObjectURL(url);
            link.remove();

            exportModal.hide();
            showAlert(`Export "${filename}" en cours...`, 'success');
        },
        error: async function(xhr, status, error) {
            console.error('[Export] Erreur:', error);
            console.error('[Export] Status HTTP:', xhr.status);

            let errMsg = 'Erreur lors de l\'export';

            // Si la réponse est un Blob (erreur serveur renvoyée car responseType: 'blob')
            if (xhr.response instanceof Blob && xhr.response.type === 'application/json') {
                try {
                    const errorText = await xhr.response.text();
                    const errorJson = JSON.parse(errorText);
                    if (errorJson.error) errMsg += `: ${errorJson.error}`;
                } catch (e) {
                    console.error('[Export] Erreur parsing JSON blob:', e);
                }
            } else if (xhr.responseJSON && xhr.responseJSON.error) {
                errMsg += `: ${xhr.responseJSON.error}`;
            } else if (xhr.status === 400) {
                errMsg += ' (paramètres invalides)';
            } else if (xhr.status === 500) {
                errMsg += ' (erreur serveur - vérifier les logs)';
            }

            console.error('[Export] Message final:', errMsg);
            showAlert(errMsg, 'danger');
        }
    });
}

// ============================================================================
// PROFILS
// ============================================================================
// PROFILS
// ============================================================================

function loadProfilesList() {
    // Charger la liste des profils disponibles (sans afficher la modal)
    $.ajax({
        url: '/api/profiles',
        type: 'GET',
        success: function(response) {
            const profiles = response.profiles || [];
            const $select = $('#profilesList');

            console.log('[Profile] Profils chargés:', profiles);

            // Garder l'option par défaut, remplacer les autres
            $select.find('option:not(:first)').remove();

            // Ajouter les profils récupérés
            if (profiles.length > 0) {
                profiles.forEach(function(profile) {
                    $select.append(`<option value="${profile}">${profile}</option>`);
                });
                console.log('[Profile] ' + profiles.length + ' profils disponibles');
            } else {
                console.log('[Profile] Aucun profil trouvé');
            }
        },
        error: function(xhr, status, error) {
            console.error('[Profile] Erreur chargement liste profils:', error);
        }
    });
}

function showProfileModal() {
    console.log('[Profile] Ouverture modal profil');

    // Recharger la liste des profils juste avant afficher la modal
    loadProfilesList();

    // Afficher la modale
    profileModal.show();
}

function saveProfile() {
    const name = $('#profileName').val() || $('#profilesList').val();

    if (!name) {
        showAlert('Veuillez entrer un nom de profil', 'warning');
        return;
    }

    console.log('[Profile] Sauvegarde profil:', name);

    // Récupérer les colonnes actuellement visibles
    const visibleCols = [];
    dataTable.columns().every(function() {
        if (this.visible()) {
            visibleCols.push(this.header().textContent);
        }
    });

    // Synchroniser les filtres avant sauvegarde
    const selectedFilterColumns = $('#filterColumnsSelector').val() || [];
    currentFilterColumns = selectedFilterColumns;

    let filterStackToSave = currentFilterStack;
    try {
        const parsedFilterStack = JSON.parse($('#filterStackEditor').val() || '[]');
        if (Array.isArray(parsedFilterStack)) {
            filterStackToSave = parsedFilterStack;
            currentFilterStack = parsedFilterStack;
        }
    } catch (e) {
        console.warn('[Profile] filter_stack editor invalide, utilisation de la stack en memoire');
    }

    $.ajax({
        url: '/api/profiles',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            name: name,
            columns: visibleCols,  // Sauvegarder colonnes réellement visibles
            filter_columns: selectedFilterColumns,
            filter_stack: filterStackToSave,
            column_aliases: currentAliasMap
        }),
        success: function(response) {
            console.log('[Profile] Sauvegardé:', response);
            showAlert(`Profil "${name}" sauvegardé (${visibleCols.length} colonnes)`, 'success');
            $('#profileName').val('');
            profileModal.hide();
            // Ne pas recharger la page - les colonnes sont déjà visibles
        },
        error: function(xhr, status, error) {
            console.error('[Profile] Erreur:', error);
            showAlert('Erreur lors de la sauvegarde du profil', 'danger');
        }
    });
}

function loadProfile() {
    const name = $('#profilesList').val();

    if (!name) {
        showAlert('Sélectionnez un profil', 'warning');
        return;
    }

    console.log('[Profile] Chargement profil:', name);

    $.ajax({
        url: `/api/profiles/${name}`,
        type: 'GET',
        dataType: 'json',
        success: function(profile) {
            console.log('[Profile] Réponse brute:', profile);
            currentProfileName = name; // Mémoriser le profil actif
            console.log('[Profile] Type:', typeof profile);
            console.log('[Profile] Keys:', Object.keys(profile));

            // colonnes à afficher
            if (profile.columns && Array.isArray(profile.columns)) {
                console.log('[Profile] Colonnes valides:', profile.columns);
                $('#columnSelector').val(profile.columns).change();
                showAlert(`Profil "${profile.name || name}" chargé (${profile.columns.length} colonnes)`, 'success');
            }

            // filters
            currentFilterColumns = profile.filter_columns || [];
            // update UI selector for filter columns
            $('#filterColumnsSelector').val(currentFilterColumns);

            currentFilterStack = profile.filter_stack || [];
            $('#filterStackEditor').val(JSON.stringify(currentFilterStack, null, 2));
            // P3.2: Afficher les filtres du profil dans la liste
            renderFilterList();

            // alias map (used server-side to resolve names)
            currentAliasMap = profile.column_aliases || {};

            // reload table to apply new filters
            dataTable.ajax.reload();

            profileModal.hide();
        },
        error: function(xhr, status, error) {
            console.error('[Profile] Erreur API:', error);
            console.log('[Profile] Status:', xhr.status);
            console.log('[Profile] Response:', xhr.responseText);
            showAlert(`Erreur lors du chargement du profil: ${error}`, 'danger');
        }
    });
}

function deleteProfile() {
    const name = $('#profilesList').val();

    if (!name) {
        showAlert('Sélectionnez un profil', 'warning');
        return;
    }

    if (!confirm(`Confirmer la suppression du profil "${name}" ?`)) {
        return;
    }

    $.ajax({
        url: `/api/profiles/${name}`,
        type: 'DELETE',
        success: function(response) {
            console.log('[Profile] Supprimé:', response);
            showAlert(`Profil "${name}" supprimé`, 'success');
            $('#profilesList').val('').change();

            // Recharger la liste des profils
            $.ajax({
                url: '/api/profiles',
                type: 'GET',
                success: function(response) {
                    const profiles = response.profiles || [];
                    const $select = $('#profilesList');
                    $select.find('option:not(:first)').remove();
                    profiles.forEach(function(profile) {
                        $select.append(`<option value="${profile}">${profile}</option>`);
                    });
                }
            });
        },
        error: function(xhr, status, error) {
            console.error('[Profile] Erreur suppression:', error);
            showAlert('Erreur lors de la suppression du profil', 'danger');
        }
    });
}

// ============================================================================
// GÉNÉRATEUR DE FILTRES
// ============================================================================

// ============================================================================
// FILTER BUILDER UTILITIES
// ============================================================================

function analyzeColumnForBooleans(column, callback) {
    // Analyser une colonne pour détecter si elle contient seulement des booléens.
    // Récupérer les 100 premières lignes pour analyser
    $.ajax({
        url: '/api/data',
        type: 'GET',
        data: {
            start: 0,
            length: 100,
            draw: 1
        },
        success: function(resp) {
            const values = new Set();
            if (resp.data) {
                resp.data.forEach(row => {
                    const val = row[column];
                    if (val !== undefined && val !== null && val !== '') {
                        values.add(String(val).toLowerCase().trim());
                    }
                });
            }

            // Vérifier si toutes les valeurs sont booléennes
            const allBool = Array.from(values).every(v =>
                ['true', 'false', '1', '0', 'yes', 'no', 'oui', 'non'].includes(v)
            );

            if (allBool && values.size > 0) {
                callback(true, Array.from(values));
            } else {
                callback(false, Array.from(values));
            }
        },
        error: function() {
            console.warn('[FilterBuilder] Erreur analyse colonne');
            callback(false, []);
        }
    });
}

function renderBooleanCheckboxes(column) {
    // Afficher des checkboxes pour True/False au lieu d'une textarea.
    const container = $('#filterBuilderCheckboxes');
    let html = '<div class="mt-2"><strong>Sélectionnez:</strong><br>';
    html += '<div class="form-check">';
    html += '<input class="form-check-input" type="checkbox" id="cbTrue" value="true">';
    html += '<label class="form-check-label" for="cbTrue">✅ True</label>';
    html += '</div>';
    html += '<div class="form-check">';
    html += '<input class="form-check-input" type="checkbox" id="cbFalse" value="false">';
    html += '<label class="form-check-label" for="cbFalse">❌ False</label>';
    html += '</div></div>';

    container.html(html).show();
    $('#filterBuilderValue').hide();
    $('#filterBuilderValues').hide().empty();
}

function loadColumnValues(column) {
    // P3.4: Récupérer les valeurs uniques de la colonne et afficher un multiselect
    const displayedOnly = $('#chkFilterDisplayedOnly').prop('checked');
    const searchVal = $('#searchInput').val() || '';

    // Payload pour récupérer les valeurs uniques (souvent via un scan des données filtrées ou non)
    const payload = {
        start: 0,
        length: 5000,
        draw: 1
    };

    // Si "Affichées uniquement", on passe les filtres courants
    if (displayedOnly) {
        payload['search[value]'] = searchVal;
        if (currentFilterStack && currentFilterStack.length > 0) {
            payload.filter_stack = JSON.stringify(currentFilterStack);
            payload.alias_map = JSON.stringify(currentAliasMap || {});
        }
        if (currentFilterColumns && currentFilterColumns.length > 0) {
            payload.filter_columns = JSON.stringify(currentFilterColumns);
        }
    }

    $.ajax({
        url: '/api/data',
        type: 'GET',
        data: payload,
        success: function(resp) {
            const values = new Set();
            if (resp.data) {
                resp.data.forEach(row => {
                    const val = row[column];
                    if (val !== undefined && val !== null && val !== '') {
                        values.add(String(val).trim());
                    }
                });
            }

            const sortedValues = Array.from(values).sort();
            console.log('[FilterBuilder] Valeurs uniques (' + (displayedOnly ? 'affichées' : 'toutes') + ') pour', column, ':', sortedValues.length);

            // Créer un dropdown multiselect
            let html = '<div class="mt-2"><strong>Sélectionnez les valeurs:</strong><br>';
            html += `<select multiple class="form-select mb-1" id="filterBuilderValuesSelect" size="${Math.min(6, sortedValues.length)}">`;
            sortedValues.forEach(v => {
                html += `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`;
            });
            html += '</select>';
            html += '<small class="text-muted d-block">Ctrl+Click pour multiselect. Le champ texte ci-dessus reste utilisable pour du texte libre.</small></div>';

            const container = $('#filterBuilderValues');
            container.html(html).show();
            // P3.4: ON NE CACHE PLUS le champ texte, on permet l'usage hybride
            $('#filterBuilderValue').show();
            $('#filterBuilderCheckboxes').hide().empty();
        },
        error: function() {
            console.warn('[FilterBuilder] Erreur récupération valeurs');
            $('#filterBuilderValue').show();
            $('#filterBuilderCheckboxes').hide().empty();
            $('#filterBuilderValues').hide().empty();
        }
    });
}

// ============================================================================
// FILTER BUILDER
// ============================================================================

function addFilterFromBuilder() {
    const column = $('#filterBuilderCol').val().trim();
    const operator = $('input[name="filterOp"]:checked').val();
    const mode = $('#filterBuilderMode').val() === 'exclude' ? 'exclude' : 'include';

    if (!column) {
        showAlert('Veuillez choisir une colonne', 'warning');
        return;
    }

    // Initialiser l'objet filtre de base
    const filterItem = {
        mode: mode,
        filters: {}
    };

    // Source de valeur: checkboxes booléens, dropdown multiselect, ou textarea texte
    let values = [];
    const checkboxContainer = $('#filterBuilderCheckboxes:visible');
    const multiSelectContainer = $('#filterBuilderValues:visible');
    const textValue = $('#filterBuilderValue').val().trim();

    if (checkboxContainer.length > 0) {
        // Mode booléen
        const checkedBoxes = checkboxContainer.find('input[type="checkbox"]:checked');
        if (checkedBoxes.length === 0) {
            showAlert('Sélectionnez au moins une valeur (True/False)', 'warning');
            return;
        }
        checkedBoxes.each(function() {
            const val = $(this).val();
            values.push(val === 'true' ? true : false);
        });
        filterItem.filters[column] = { values };
    } else {
        // Logique hybride (P3.4): Multiselect ET/OU Texte libre
        let selectedValues = [];
        if (multiSelectContainer.length > 0) {
            const selectVal = $('#filterBuilderValuesSelect').val();
            if (selectVal && selectVal.length > 0) {
                selectedValues = selectVal;
            }
        }

        if (operator === 'values') {
            // Fusionner texte libre et sélection dropdown
            let manualValues = textValue ? textValue.split(',').map(v => v.trim()).filter(v => v) : [];
            values = [...new Set([...manualValues, ...selectedValues])];

            if (values.length === 0) {
                showAlert('Veuillez saisir une valeur ou en sélectionner une dans la liste', 'warning');
                return;
            }
            filterItem.filters[column] = { values };
        } else if (operator === 'search') {
            if (!textValue) {
                showAlert('Veuillez saisir le texte à rechercher', 'warning');
                return;
            }
            filterItem.filters[column] = { search: textValue };
        } else if (operator === 'regex') {
            if (!textValue) {
                showAlert('Veuillez saisir la regex', 'warning');
                return;
            }
            filterItem.filters[column] = { search: textValue, is_regex: true };
        }
    }

    // Ajouter à la pile
    currentFilterStack.push(filterItem);
    console.log('[FilterBuilder] Stack mise à jour:', currentFilterStack);

    // Mettre à jour le textarea JSON
    $('#filterStackEditor').val(JSON.stringify(currentFilterStack, null, 2));

    // Réinitialiser le formulaire
    $('#filterBuilderCol').val('');
    $('#filterBuilderValue').val('');
    $('#filterBuilderCheckboxes').empty().hide();
    $('#filterBuilderValues').empty().hide();
    $('#filterBuilderMode').val('include');
    $('#opValues').prop('checked', true);

    // Mettre à jour l'affichage
    renderFilterList();
    const modeLabel = mode === 'exclude' ? 'exclude' : 'include';
    showAlert(`Filtre ${modeLabel} ajouté sur "${column}"`, 'success');
}

function renderFilterList() {
    const container = $('#filterBuilderList');
    container.empty();

    if (!currentFilterStack || currentFilterStack.length === 0) {
        container.html('<p class="text-muted">Aucun filtre ajouté</p>');
        return;
    }

    let html = '<h6>📜 Filtres actuels:</h6><ul class="list-group">';

    currentFilterStack.forEach((item, idx) => {
        const mode = item.mode || 'include';
        const filters = item.filters || {};
        const cols = Object.keys(filters);
        const summary = cols.length > 0 ? cols.join(', ') : '(vide)';

        // Déterminer si le bouton up/down doit être actif
        const canMoveUp = idx > 0;
        const canMoveDown = idx < currentFilterStack.length - 1;

        html += `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <span class="badge badge-pill" style="background-color: ${mode === 'include' ? '#28a745' : '#dc3545'};">${mode}</span>
                    <strong>${summary}</strong>
                </div>
                <div>
                    <button class="btn btn-sm btn-secondary" onclick="moveFilterUp(${idx})" ${canMoveUp ? '' : 'disabled'}>▲</button>
                    <button class="btn btn-sm btn-secondary" onclick="moveFilterDown(${idx})" ${canMoveDown ? '' : 'disabled'}>▼</button>
                    <button class="btn btn-sm btn-danger" onclick="removeFilterAt(${idx})">🗑️</button>
                </div>
            </li>
        `;
    });

    html += '</ul>';
    container.html(html);
}

function moveFilterUp(idx) {
    if (idx > 0 && idx < currentFilterStack.length) {
        // Swap avec élément précédent
        const tmp = currentFilterStack[idx];
        currentFilterStack[idx] = currentFilterStack[idx - 1];
        currentFilterStack[idx - 1] = tmp;
        console.log('[FilterBuilder] Filtre déplacé up:', idx);
        $('#filterStackEditor').val(JSON.stringify(currentFilterStack, null, 2));
        renderFilterList();
    }
}

function moveFilterDown(idx) {
    if (idx >= 0 && idx < currentFilterStack.length - 1) {
        // Swap avec élément suivant
        const tmp = currentFilterStack[idx];
        currentFilterStack[idx] = currentFilterStack[idx + 1];
        currentFilterStack[idx + 1] = tmp;
        console.log('[FilterBuilder] Filtre déplacé down:', idx);
        $('#filterStackEditor').val(JSON.stringify(currentFilterStack, null, 2));
        renderFilterList();
    }
}

function removeFilterAt(idx) {
    if (idx >= 0 && idx < currentFilterStack.length) {
        const removed = currentFilterStack.splice(idx, 1);
        console.log('[FilterBuilder] Filtre supprimé:', removed[0]);
        $('#filterStackEditor').val(JSON.stringify(currentFilterStack, null, 2));
        renderFilterList();
        showAlert('Filtre supprimé', 'info');
    }
}

// ============================================================================
// UTILITAIRES
// ============================================================================

function getVisibleColumns() {
    const selected = $('#columnSelector').val();
    return selected && selected.length > 0 ? selected : currentColumns;
}

function resetFilters() {
    console.log('[Filters] Réinitialisation');
    $('#searchInput').val('');
    $('#columnSelector').val(currentColumns).change();

    // vider les filtres personnalisés
    currentFilterColumns = [];
    currentFilterStack = [];
    currentProfileName = null; // Réinitialiser le profil actif
    currentAliasMap = {};
    $('#filterColumnsSelector').val([]);
    $('#filterStackEditor').val('[]');

    dataTable.ajax.reload();
    updateDataInfo();
}

function reloadData() {
    console.log('[Data] Rechargement...');

    $.ajax({
        url: '/api/reload',
        type: 'POST',
        success: function(response) {
            console.log('[Data] Rechargé:', response);
            showAlert(`Données rechargées: ${response.rows} lignes`, 'success');
            location.reload();
        },
        error: function(xhr, status, error) {
            console.error('[Data] Erreur:', error);
            showAlert('Erreur lors du rechargement', 'danger');
        }
    });
}

function updateDataInfo() {
    const info = dataTable.page.info();
    if (info) {
        const msg = `${info.recordsFiltered} / ${info.recordsTotal} lignes affichées`;
        $('#dataInfo').text(msg);
    }
}

function showStats() {
    console.log('[Stats] Chargement statistiques...');

    $.ajax({
        url: '/api/stats',
        type: 'GET',
        success: function(stats) {
            console.log('[Stats]', stats);

            let html = `<h5>📊 Statistiques</h5>`;
            html += `<p><strong>Total:</strong> ${stats.total_rows} lignes × ${stats.total_columns} colonnes</p>`;
            html += `<p><strong>Colonnes:</strong> ${stats.columns.join(', ')}</p>`;
            html += `<p><strong>Aperçu (5 premières lignes):</strong></p>`;
            html += `<pre style="font-size:0.8rem;max-height:300px;overflow:auto;">`;
            stats.sample.forEach(row => {
                html += row.join(' | ') + '\n';
            });
            html += `</pre>`;

            showModal('Statistiques', html);
        },
        error: function(xhr, status, error) {
            console.error('[Stats] Erreur:', error);
            showAlert('Erreur lors du chargement des statistiques', 'danger');
        }
    });
}

function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert" style="margin-bottom:1rem;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // Insérer en haut du container
    $('.container-fluid').prepend(alertHtml);

    // Auto-dismiss après 5s si success/info
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            $('.alert:first').fadeOut(function() { $(this).remove(); });
        }, 5000);
    }
}

function showModal(title, content) {
    // Créer modal simple
    const modal = $(`
        <div class="modal fade" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                </div>
            </div>
        </div>
    `);

    $('body').append(modal);
    new bootstrap.Modal(modal[0]).show();
    modal.on('hidden.bs.modal', function() { $(this).remove(); });
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

// Logging helper
console.log('%c[UnityAssetsManager]', 'color: green; font-weight: bold;', 'Client initialisé');
