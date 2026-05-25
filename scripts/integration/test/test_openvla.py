# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 21 mai 2026
# Objectif    : Vérifier le chargement du modèle openvla-7b sur GPU (CUDA) et
#               l'utilisation VRAM après initialisation.
# =============================================================================
from transformers import AutoModelForVision2Seq, AutoProcessor
import torch

MODEL_PATH = r"C:\Users\Etudiant\models\openvla-7b"
print("Loading processor...")
processor = AutoProcessor.from_pretrained(MODEL_PATH,trust_remote_code=True)
print("✅ Processor loaded.")
print("Loading model...")
model = AutoModelForVision2Seq.from_pretrained(MODEL_PATH,
                                               torch_dtype=torch.float16,
                                               device_map="cuda",                                               
                                                trust_remote_code=True)
print(f"✅ Model loaded. in {model.device}")
print(f"✅ VRAM used: {torch.cuda.memory_allocated() / 1e9:.2f} GB")