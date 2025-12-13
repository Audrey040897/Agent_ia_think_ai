from typing import Dict, Any
import os
import requests
from dotenv import load_dotenv
from models.episode import Episode

# Charger les variables d'environnement (.env)
load_dotenv()

SYMFONY_API_URL = os.getenv("SYMFONY_API_URL")
SYMFONY_API_TOKEN = os.getenv("SYMFONY_API_TOKEN")


def build_payload(episode: Episode) -> Dict[str, Any]:
    """
    Transforme notre modèle Episode en payload pour l'API Symfony.
    À ADAPTER en fonction des champs attendus côté Symfony.
    """
    return {
        "title": episode.title,
        "audioUrl": episode.audio_url,
        "duration": episode.duration,
        "transcript": episode.transcript,
        "keywords": episode.keywords,
        "category": episode.category,
        "coverImage": episode.cover_image,
        "contributorEmail": episode.contributor_email,
        "qualityStatus": episode.quality_status,
        "qualityScore": episode.quality_score,
        "status": episode.status,  # ex: "draft" ou "ready_for_review"
    }


def publish_episode(episode: Episode) -> Dict[str, Any]:
    """
    Envoie l'épisode vers le back-office Symfony.
    Retourne un dict avec un statut et des détails.

    Le but : ne JAMAIS faire planter l'API même si Symfony ne répond pas.
    """

    # Si l'URL Symfony n'est pas configurée, on ne tente rien
    if not SYMFONY_API_URL:
        return {
            "status": "NOT_CONFIGURED",
            "details": "SYMFONY_API_URL non définie dans le fichier .env. Publication non envoyée."
        }

    payload = build_payload(episode)

    headers = {
        "Content-Type": "application/json",
    }

    # Si un token d'API est disponible, on l'ajoute (à adapter selon Symfony : Bearer, X-API-KEY, etc.)
    if SYMFONY_API_TOKEN:
        headers["Authorization"] = f"Bearer {SYMFONY_API_TOKEN}"

    try:
        response = requests.post(SYMFONY_API_URL, json=payload, headers=headers, timeout=10)

        if 200 <= response.status_code < 300:
            return {
                "status": "SENT",
                "http_status": response.status_code,
                "response": safe_json(response)
            }
        else:
            return {
                "status": "ERROR",
                "http_status": response.status_code,
                "response": safe_json(response)
            }

    except Exception as e:
        # Pour le hackathon : on loggue l'erreur mais on ne casse rien
        return {
            "status": "FAILED",
            "details": f"Erreur lors de l'appel à Symfony : {e}"
        }


def safe_json(response: requests.Response) -> Any:
    """
    Essaie de décoder le JSON de réponse, sinon renvoie le texte brut.
    """
    try:
        return response.json()
    except Exception:
        return response.text
