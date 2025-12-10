from pathlib import Path
from fastapi import UploadFile
import shutil

# Dossiers de travail
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_RAW_DIR = BASE_DIR / "uploads" / "raw"
UPLOAD_FINAL_DIR = BASE_DIR / "uploads" / "final"
RESOURCES_DIR = BASE_DIR / "resources"


async def save_raw_file(file: UploadFile) -> str:
    """Sauvegarde le fichier uploadé dans uploads/raw/ et retourne son chemin."""
    UPLOAD_RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = UPLOAD_RAW_DIR / file.filename

    with open(raw_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return str(raw_path)


def build_final_audio(raw_path: str) -> dict:
    """
    V1 simplifiée :
    - copie le fichier brut (mp3, mp4, etc.) dans uploads/final/
    - pas de conversion ni ffmpeg pour l'instant
    """
    UPLOAD_FINAL_DIR.mkdir(parents=True, exist_ok=True)
    final_path = UPLOAD_FINAL_DIR / f"final_{Path(raw_path).name}"

    # Simple copie du fichier
    shutil.copyfile(raw_path, final_path)

    # Valeurs fictives pour la V1
    duration_seconds = 0
    quality_score = 80
    quality_status = "OK"

    return {
        "final_path": str(final_path),
        "duration_seconds": duration_seconds,
        "quality_score": quality_score,
        "quality_status": quality_status,
    }
