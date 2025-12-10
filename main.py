

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from services import audio, stt, nlp, publish
from models.episode import Episode

app = FastAPI(
    title="Agent IA Inspiron",
    description="Pipeline IA pour automatiser le traitement des podcasts Inspiron",
    version="0.1.0"
)

@app.get("/")
def health():
    return {"status": "ok", "message": "Agent IA opérationnel"}

@app.post("/upload")
async def upload_episode(
    file: UploadFile = File(...),
    contributor_email: str = Form(...)
):
    # 1. Sauvegarde du fichier brut (mp3, mp4, etc.)
    raw_path = await audio.save_raw_file(file)

    # 2. Audio final + qualité (V1 : copie + éventuelle conversion en wav)
    audio_info = audio.build_final_audio(raw_path)

    # 3. Transcription (pour l'instant : simulée dans stt.py)
    transcript = stt.transcribe(audio_info["final_path"])

    # 4. NLP : mots-clés, catégorie, pochette
    keywords = nlp.extract_keywords(transcript)
    category = nlp.guess_category(transcript)
    cover_image = nlp.map_category_to_cover(category)

    # 5. Construire un épisode (brouillon)
    episode = Episode(
        title="Titre provisoire",
        audio_url=audio_info["final_path"],
        duration=audio_info["duration_seconds"],
        transcript=transcript,
        keywords=keywords,
        category=category,
        cover_image=cover_image,
        contributor_email=contributor_email,
        quality_status=audio_info["quality_status"],
        quality_score=audio_info["quality_score"],
        status="draft",
    )

    return JSONResponse({
        "steps": {
            "audio": "OK",
            "transcription": "OK (simulée)",
            "nlp": "OK",
            "publication": "NOT_SENT"
        },
        "episode_preview": episode.dict()
    })
