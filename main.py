from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from services import audio, stt, nlp, publish, contributors
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

    # 2. Audio final + qualité (intro + épisode + analyse)
    audio_info = audio.build_final_audio(raw_path)

    # 3. Transcription (Whisper) – sur la version finale
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
            "transcription": "OK",
            "nlp": "OK",
            "publication": "NOT_SENT"
        },
        "episode_preview": episode.dict()
    })


@app.post("/check-audio-quality")
async def check_audio_quality(file: UploadFile = File(...)):
    """
    Vérifie uniquement la qualité audio du fichier brut (sans générique),
    selon les critères éditoriaux.
    """
    # 1. Sauvegarde du fichier brut
    raw_path = await audio.save_raw_file(file)

    # 2. Analyse sur le fichier brut
    quality_info = audio.analyze_raw_audio(raw_path)

    return JSONResponse({
        "step": "audio_quality_raw_only",
        "file": quality_info["path"],
        "duration_seconds": quality_info["duration_seconds"],
        "quality_status": quality_info["quality_status"],
        "quality_score": quality_info["quality_score"],
        "quality_details": quality_info["quality_details"],
    })
