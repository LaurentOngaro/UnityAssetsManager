# ============================================================================
# runManualChecklist.ps1 - Checklist manuelle UnityAssetsManager
# ============================================================================
# Usage:
#   pwsh -NoProfile -File _Helpers/04_Assets/UnityAssetsManager/_helpers/runManualChecklist.ps1
#   pwsh -NoProfile -File _Helpers/04_Assets/UnityAssetsManager/_helpers/runManualChecklist.ps1 -BaseUrl http://localhost:5000
#   pwsh -NoProfile -File _Helpers/04_Assets/UnityAssetsManager/_helpers/runManualChecklist.ps1 -OutputDir exports/manual_checklist
#
# Description:
#   Exécute les contrôles scriptés de non-régression pour les exports,
#   les profils et le flux include/exclude.
# ============================================================================

param(
    [string]$BaseUrl = "http://localhost:5003",
    [string]$OutputDir = "exports/manual_checklist"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$appRoot = Split-Path -Parent $scriptRoot
$resolvedOutputDir = Join-Path $appRoot $OutputDir

if (-not (Test-Path $resolvedOutputDir)) {
    New-Item -ItemType Directory -Path $resolvedOutputDir | Out-Null
}

$checks = New-Object System.Collections.Generic.List[object]

function Add-CheckResult {
    param(
        [string]$Name,
        [string]$Status,
        [string]$Details
    )

    $checks.Add([PSCustomObject]@{
            Name = $Name
            Status = $Status
            Details = $Details
        })
}

function Invoke-ApiJson {
    param(
        [string]$Method,
        [string]$Path,
        [object]$Body = $null
    )

    $uri = "$BaseUrl$Path"
    if ($null -eq $Body) {
        return Invoke-RestMethod -Method $Method -Uri $uri -TimeoutSec 20
    }

    $json = $Body | ConvertTo-Json -Depth 10
    return Invoke-RestMethod -Method $Method -Uri $uri -ContentType "application/json" -Body $json -TimeoutSec 20
}

Write-Host "[Manual Checklist] BaseUrl: $BaseUrl" -ForegroundColor Cyan
Write-Host "[Manual Checklist] OutputDir: $resolvedOutputDir" -ForegroundColor Cyan

try {
    $templatesResponse = Invoke-ApiJson -Method GET -Path "/api/templates"
    $templates = @($templatesResponse.templates)
    Add-CheckResult -Name "API reachable" -Status "PASS" -Details "/api/templates OK ($($templates.Count) templates)"
}
catch {
    Add-CheckResult -Name "API reachable" -Status "FAIL" -Details $_.Exception.Message
    $checks | Format-Table -AutoSize
    throw "Impossible de joindre UnityAssetsManager. Lancer l'app avant ce script."
}

$profileName = "manual_checklist_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$profilePayload = @{
    name = $profileName
    columns = @("DisplayName", "DisplayPublisher", "DisplayCategory", "Version")
    filter_columns = @("DisplayCategory", "DisplayPublisher")
    filter_stack = @(
        @{
            mode = "include"
            filters = @{
                DisplayCategory = @{
                    values = @("Tools")
                }
            }
            search_term = ""
        },
        @{
            mode = "exclude"
            filters = @{
                DisplayPublisher = @{
                    values = @("PublisherB")
                }
            }
            search_term = ""
        }
    )
}

try {
    $saveResult = Invoke-ApiJson -Method POST -Path "/api/profiles" -Body $profilePayload
    if ($saveResult.success -eq $true) {
        Add-CheckResult -Name "Save profile" -Status "PASS" -Details "Profil '$profileName' sauvegardé"
    }
    else {
        Add-CheckResult -Name "Save profile" -Status "FAIL" -Details "Réponse inattendue"
    }
}
catch {
    Add-CheckResult -Name "Save profile" -Status "FAIL" -Details $_.Exception.Message
}

try {
    $loadedProfile = Invoke-ApiJson -Method GET -Path "/api/profiles/$profileName"
    $modes = @($loadedProfile.filter_stack | ForEach-Object { $_.mode })
    $hasInclude = $modes -contains "include"
    $hasExclude = $modes -contains "exclude"

    if ($hasInclude -and $hasExclude) {
        Add-CheckResult -Name "Load profile" -Status "PASS" -Details "Stack include/exclude restaurée"
    }
    else {
        Add-CheckResult -Name "Load profile" -Status "FAIL" -Details "Modes manquants: $($modes -join ', ')"
    }
}
catch {
    Add-CheckResult -Name "Load profile" -Status "FAIL" -Details $_.Exception.Message
}

$templateMap = @{
    csv = ($templates | Where-Object { $_.name -match "csv" } | Select-Object -First 1)
    md = ($templates | Where-Object { $_.name -match "markdown|liste|table" } | Select-Object -First 1)
    json = ($templates | Where-Object { $_.name -match "json" } | Select-Object -First 1)
    txt = ($templates | Where-Object { $_.name -match "texte|text|simple" } | Select-Object -First 1)
}

foreach ($format in @("csv", "md", "json", "txt")) {
    $template = $templateMap[$format]
    if ($null -eq $template) {
        Add-CheckResult -Name "Batch export $format" -Status "SKIP" -Details "Aucun template disponible pour ce format"
        continue
    }

    $fileName = "manual_export_$format"
    $payload = @{
        template = $template.name
        columns = @("DisplayName", "DisplayPublisher", "DisplayCategory", "Version")
        search = ""
        filter_stack = $profilePayload.filter_stack
        alias_map = @{}
        output_dir = $resolvedOutputDir
        file_name = $fileName
    }

    try {
        $batch = Invoke-ApiJson -Method POST -Path "/api/batch-export" -Body $payload
        if ($batch.success -ne $true) {
            Add-CheckResult -Name "Batch export $format" -Status "FAIL" -Details "Réponse success=false"
            continue
        }

        $exportPath = [string]$batch.path
        if ([string]::IsNullOrWhiteSpace($exportPath) -or -not (Test-Path $exportPath)) {
            Add-CheckResult -Name "Batch export $format" -Status "FAIL" -Details "Fichier non trouvé"
            continue
        }

        $actualExt = [System.IO.Path]::GetExtension($exportPath).TrimStart(".").ToLowerInvariant()
        if ($actualExt -eq $format) {
            Add-CheckResult -Name "Batch export $format" -Status "PASS" -Details "OK: $exportPath"
        }
        else {
            Add-CheckResult -Name "Batch export $format" -Status "FAIL" -Details "Extension attendue '$format', obtenue '$actualExt'"
        }
    }
    catch {
        Add-CheckResult -Name "Batch export $format" -Status "FAIL" -Details $_.Exception.Message
    }
}

try {
    $null = Invoke-ApiJson -Method DELETE -Path "/api/profiles/$profileName"
    Add-CheckResult -Name "Delete profile" -Status "PASS" -Details "Profil temporaire supprimé"
}
catch {
    Add-CheckResult -Name "Delete profile" -Status "FAIL" -Details $_.Exception.Message
}

Write-Host ""
Write-Host "=== Résultats API (scriptés) ===" -ForegroundColor Green
$checks | Format-Table -AutoSize

Write-Host ""
Write-Host "=== Checklist UI manuelle (à faire dans le navigateur) ===" -ForegroundColor Yellow
Write-Host "[ ] Ouvrir l'application et créer un filtre include sur DisplayCategory=Tools"
Write-Host "[ ] Ajouter un filtre exclude sur DisplayPublisher=PublisherB"
Write-Host "[ ] Cliquer Apply et vérifier que la table ne contient plus PublisherB"
Write-Host "[ ] Sauvegarder un profil depuis l'UI"
Write-Host "[ ] Recharger ce profil et vérifier que la stack include/exclude est intacte"
Write-Host "[ ] Ouvrir l'export modal et vérifier les compteurs de lignes"

$failed = @($checks | Where-Object { $_.Status -eq "FAIL" }).Count
if ($failed -gt 0) {
    throw "Checklist scriptée: $failed échec(s)."
}

Write-Host ""
Write-Host "Checklist scriptée terminée sans échec." -ForegroundColor Green
