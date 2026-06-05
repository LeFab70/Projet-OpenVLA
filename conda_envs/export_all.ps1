# =============================================================================
# Exporte tous les environnements Conda du projet OpenVLA (complets avec pip)
# Usage (PowerShell, racine du projet) : .\export_all.ps1
# =============================================================================

$ErrorActionPreference = "Stop"
$OutDir = Join-Path $PSScriptRoot "conda_envs"
$envs = @("env_zivid", "env_ur", "env_integration")

# ─────────────────────────────────────────
# Vérifications
# ─────────────────────────────────────────
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Error "conda introuvable. Lance ce script sur le PC Windows avec Miniconda/Anaconda."
    exit 1
}

if (-not (Test-Path $OutDir)) {
    Write-Host "Création dossier : $OutDir"
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

Write-Host "═" * 60
Write-Host "EXPORT COMPLETS CONDA → $OutDir"
Write-Host "═" * 60

# ─────────────────────────────────────────
# Boucle export
# ─────────────────────────────────────────
foreach ($name in $envs) {
    Write-Host "`n✓ $name"
    Write-Host "─" * 50
    
    $outFile = Join-Path $OutDir "$name.yaml"
    $reqFile = Join-Path $OutDir "$name-requirements.txt"
    
    try {
        # Activer environment
        conda activate $name 2>&1 | Out-Null
        
        # Export COMPLET (conda + pip)
        Write-Host "  Exporting YAML (conda + pip)..."
        conda env export | Out-File -FilePath $outFile -Encoding utf8 -Force
        Write-Host "  ✅ $outFile"
        
        # Export pip uniquement (bonus)
        Write-Host "  Exporting pip requirements..."
        pip freeze | Out-File -FilePath $reqFile -Encoding utf8 -Force
        Write-Host "  ✅ $reqFile"
        
    } catch {
        Write-Host "  ❌ Erreur : $_"
    }
}

Write-Host "`n" + "═" * 60
Write-Host "✅ Export terminé !"
Write-Host "═" * 60
Write-Host "`nFichiers créés dans : $OutDir"
Write-Host "  • *.yaml : export complet Conda (pour conda env create -f)"
Write-Host "  • *-requirements.txt : packages pip (pour pip install -r)"
Write-Host "`nProchaines étapes :"
Write-Host "  1. Vérifie les fichiers : ls $OutDir"
Write-Host "  2. Commit si OK : git add $OutDir && git commit -m 'Export environments'"