from pathlib import Path
import whisper

# On charge le modèle Whisper une seule fois
model = whisper.load_model("base")


def transcribe(audio_path: str) -> str:
    """
    Transcrit un fichier audio ou vidéo avec Whisper.
    En cas d'erreur, retourne un message explicite sans casser l'API.
    """
    audio_path_str = str(Path(audio_path))

    # 1) Vérifier que le fichier existe vraiment
    p = Path(audio_path_str)
    if not p.exists():
        return f"[Transcription impossible] Fichier introuvable : {audio_path_str}"

    try:
        print(f"🔍 Transcription en cours : {audio_path_str}")

        result = model.transcribe(audio_path_str, language="fr", fp16=False)
        text = result.get("text", "").strip()

        if not text:
            return "[Transcription vide] Aucun texte détecté dans l'audio."

        return text

    except Exception:
        return (
            "[Transcription non disponible pour cet épisode] "
            "La transcription automatique sera activée dans la prochaine version de l’agent."
        )
