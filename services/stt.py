"""
Module de transcription audio.

V1 :
- Essaie d'utiliser Whisper (modèle "small") pour une vraie transcription.
- Si Whisper ou ffmpeg ne sont pas dispos, on revient à une transcription simulée
  pour ne jamais casser le pipeline.
"""

from pathlib import Path

try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception:
    whisper = None
    WHISPER_AVAILABLE = False


# On charge le modèle une seule fois si possible
MODEL = None
if WHISPER_AVAILABLE:
    try:
        MODEL = whisper.load_model("small")  # tu peux mettre "base" ou "tiny" si c'est trop lourd
    except Exception:
        MODEL = None
        WHISPER_AVAILABLE = False


def transcribe(audio_path: str) -> str:
    """
    Transcrit un fichier audio/vidéo avec Whisper si possible.
    Sinon, renvoie une transcription simulée.
    """
    # Si Whisper n'est pas dispo (problème d'installation, ffmpeg manquant, etc.)
    if not WHISPER_AVAILABLE or MODEL is None:
        return f"[Transcription simulée] Whisper non disponible. Fichier : {audio_path}"

    try:
        # Whisper gère mp3, wav, mp4, m4a, etc.
        audio_path_str = str(Path(audio_path))
        result = MODEL.transcribe(audio_path_str, language="fr", fp16=False)
        text = result.get("text", "").strip()

        if not text:
            return f"[Transcription vide] Whisper n'a rien détecté. Fichier : {audio_path}"

        return text

    except Exception as e:
        # En cas d'erreur (ex : ffmpeg absent), on ne casse pas l'API
        return f"[Transcription simulée après erreur Whisper : {e}] Fichier : {audio_path}"

