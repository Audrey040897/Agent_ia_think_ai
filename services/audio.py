from pathlib import Path
from typing import Dict, Any

from fastapi import UploadFile
import shutil

from pydub import AudioSegment

# Dossiers
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_RAW_DIR = BASE_DIR / "uploads" / "raw"
UPLOAD_FINAL_DIR = BASE_DIR / "uploads" / "final"
RESOURCES_DIR = BASE_DIR / "resources"

INTRO_PATH = RESOURCES_DIR / "intro.mp3"
OUTRO_PATH = RESOURCES_DIR / "outro.mp3"


# ------------------------------------------------------------
# 1) Sauvegarde du fichier brut
# ------------------------------------------------------------

async def save_raw_file(file: UploadFile) -> str:
    UPLOAD_RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = UPLOAD_RAW_DIR / file.filename

    with open(raw_path, "wb") as f:
        f.write(await file.read())

    return str(raw_path)


# ------------------------------------------------------------
# 2) Analyse ÉDITORIALE — uniquement sur l'audio principal
# ------------------------------------------------------------

def _estimate_noise_floor(audio: AudioSegment, frame_ms=200) -> float:
    """Analyse du bruit de fond."""
    if len(audio) < frame_ms:
        return float(audio.dBFS)

    samples = []
    for i in range(0, len(audio), frame_ms):
        samples.append(audio[i:i+frame_ms].dBFS)

    samples.sort()
    quiet_frames = samples[:max(1, int(len(samples) * 0.2))]

    return sum(quiet_frames) / len(quiet_frames)

def _compute_tech_info(audio: AudioSegment, path: Path) -> Dict[str, Any]:
    """Infos techniques de base sur le fichier audio."""
    channels = audio.channels
    sample_rate = audio.frame_rate
    bit_depth = audio.sample_width * 8  # taille d'échantillon (bytes → bits)
    bitrate_kbps = int(round(sample_rate * bit_depth * channels / 1000))

    return {
        "file_name": path.name,
        "suffix": path.suffix.lower(),
        "channels": channels,
        "sample_rate_hz": sample_rate,
        "bit_depth": bit_depth,
        "bitrate_kbps_approx": bitrate_kbps,
    }

def _analyze_audio_main(path: Path) -> Dict[str, Any]:
    """Analyse SEULEMENT du podcast brut, sans génériques."""
    audio = AudioSegment.from_file(path)
    duration = len(audio) / 1000
    loudness = audio.dBFS
    peak = audio.max_dBFS
    noise = _estimate_noise_floor(audio)

    # 👉 Infos techniques pour Streamlit
    tech = _compute_tech_info(audio, path)

    score = 100
    checks: Dict[str, Any] = {}

    # Durée
    if 4 * 60 <= duration <= 15 * 60:
        checks["duration"] = {"ok": True}
    else:
        checks["duration"] = {
            "ok": False,
            "message": "Durée hors zone idéale (4–15 min)."
        }
        score -= 10

    # Loudness
    if -22 <= loudness <= -14:
        checks["loudness"] = {"ok": True}
    else:
        checks["loudness"] = {
            "ok": False,
            "message": f"Loudness {loudness:.1f} dBFS."
        }
        score -= 15

    # Peak
    if peak <= -1:
        checks["peak"] = {"ok": True}
    else:
        checks["peak"] = {
            "ok": False,
            "message": f"Pic {peak:.1f} dBFS (risque saturation)."
        }
        score -= 20

    # Bruit de fond
    if noise < -45:
        checks["noise"] = {"ok": True}
    else:
        checks["noise"] = {
            "ok": False,
            "message": f"Bruit {noise:.1f} dBFS."
        }
        score -= 20

    score = max(0, min(100, score))
    status = "OK" if score >= 80 else "A_REVOIR" if score >= 60 else "REFUSE"

    return {
        "duration_seconds": int(duration),
        "loudness_dbfs": loudness,
        "peak_dbfs": peak,
        "noise_floor_dbfs": noise,
        "quality_score": score,
        "quality_status": status,
        "checks": checks,
        "tech": tech,          # 👈 IMPORTANT pour Streamlit
        "path": str(path),
    }

# ------------------------------------------------------------
# 3) Construction du fichier final avec génériques
# ------------------------------------------------------------

def _combine_audio(main_audio: Path) -> Path:
    """intro + épisode + outro (optionnel)"""

    UPLOAD_FINAL_DIR.mkdir(parents=True, exist_ok=True)

    suffix = main_audio.suffix or ".mp3"
    final_path = UPLOAD_FINAL_DIR / f"final_{main_audio.stem}{suffix}"

    segments = []

    # Intro
    if INTRO_PATH.exists():
        segments.append(AudioSegment.from_file(INTRO_PATH))

    # Épisode principal
    main = AudioSegment.from_file(main_audio)
    segments.append(main)

    # Outro désactivé pour le moment
    #if OUTRO_PATH.exists():
      #  segments.append(AudioSegment.from_file(OUTRO_PATH))

    final = segments[0]
    for seg in segments[1:]:
        final += seg

    # Export
    final.export(final_path, format=suffix.replace(".", ""))

    return final_path


# ------------------------------------------------------------
# 4) Fonction principale
# ------------------------------------------------------------

def build_final_audio(raw_path: str) -> dict:
    source = Path(raw_path)

    # 1) Analyse uniquement du podcast brut
    analysis = _analyze_audio_main(source)

    # 2) Création du fichier final avec génériques
    final_path = _combine_audio(source)

    return {
        "final_path": str(final_path),
        "duration_seconds": analysis["duration_seconds"],
        "quality_score": analysis["quality_score"],
        "quality_status": analysis["quality_status"],
        "quality_details": analysis,
    }
