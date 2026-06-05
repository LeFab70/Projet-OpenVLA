# Environnements Conda — Projet OpenVLA

Fichiers YAML des 4 environnements Python **3.11** utilisés sur le poste Windows du stage.

| Fichier | Environnement | Usage |
|---------|---------------|--------|
| `env_zivid.yaml` | `env_zivid` | Caméra Zivid seule |
| `env_ur.yaml` | `env_ur` | Robot UR (RTDE) seul |
| `env_integration.yaml` | `env_integration` | Zivid + UR |
| `env_openvla.yaml` | `env_openvla` | Inférence OpenVLA + pipeline complet |

## Recréer un environnement

```powershell
conda env create -f conda_envs\env_zivid.yaml
conda env update -f conda_envs\env_openvla.yaml --prune
```

## Régénérer les YAML depuis ta machine (export exact)

Sur le **PC Windows** où Conda est installé, à la racine du projet :

```powershell
.\conda_envs\export_all.ps1
```

Cela écrase les `.yaml` avec `conda env export --from-history` (portable) et un export complet pour `env_openvla`.

## Notes

- **env_openvla** : PyTorch **nightly cu128** (RTX 5090 / Blackwell). Après `conda env create`, si CUDA manque :
  ```powershell
  conda activate env_openvla
  pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
  pip install transformers==4.40.1 --force-reinstall
  ```
- Modèle : `huggingface-cli download openvla/openvla-7b --local-dir C:\Users\Etudiant\models\openvla-7b`
- Voir aussi `scripts/utils.txt` et README (section Jour 04 / Jour 06).
