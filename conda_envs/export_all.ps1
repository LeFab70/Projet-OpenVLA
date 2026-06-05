# Exporte les 4 environnements Conda du projet OpenVLA vers conda_envs/*.yaml
# Usage (PowerShell, racine du projet) : .\conda_envs\export_all.ps1

$ErrorActionPreference = "Stop"
$OutDir = Join-Path $PSScriptRoot "."
$envs = @("env_zivid", "env_ur", "env_integration", "env_openvla")

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Error "conda introuvable. Lance ce script sur le PC Windows avec Miniconda/Anaconda."
}

Write-Host "Export vers : $OutDir"
foreach ($name in $envs) {
    $outFile = Join-Path $OutDir "$name.yaml"
    Write-Host "`n=== $name ==="
    conda activate $name
    if ($name -eq "env_openvla") {
        # Export complet pour capturer pip (torch nightly, transformers pin)
        conda env export | Out-File -FilePath $outFile -Encoding utf8
        Write-Host "  -> export complet : $outFile"
    } else {
        conda env export --from-history | Out-File -FilePath $outFile -Encoding utf8
        Write-Host "  -> export --from-history : $outFile"
    }
}
Write-Host "`nTerminé. Vérifie les fichiers puis commit si besoin."
