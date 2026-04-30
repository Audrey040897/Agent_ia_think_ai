"""
nlp_v2.py — Version LLM de l'intelligence éditoriale Inspiron
--------------------------------------------------------------
Remplace le NLP basé sur des règles (nlp.py V1) par des appels
à GPT-4o-mini via l'API OpenAI.

Améliorations V2 vs V1 :
- Extraction de mots-clés sémantique (comprend le sens, pas juste le matching)
- Catégorisation par compréhension du discours global
- Généralise sur des termes non présents dans le lexique V1
- Fallback automatique vers la V1 en cas d'erreur API

Prérequis :
    pip install openai python-dotenv

Variables d'environnement (.env) :
    OPENAI_API_KEY=sk-...
"""

import os
import json
from typing import List
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

# Fallback V1 en cas d'erreur API
from services.nlp import (
    extract_keywords as extract_keywords_v1,
    guess_category as guess_category_v1,
)

# Charger la clé API depuis .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- Catégories éditoriales Inspiron ----------
CATEGORIES = [
    "Régulation intérieure et bien-être",
    "Communication, relations et intelligence collective",
    "Inspiration, sens et transformation",
]

# ---------- Mapping catégorie → pochette ----------
CATEGORY_TO_COVER = {
    "Régulation intérieure et bien-être": "Régulation intérieure et bien-être.png",
    "Communication, relations et intelligence collective": "Communication, relations et intelligence collective.png",
    "Inspiration, sens et transformation": "Inspiration, sens et transformation.png",
}


# ============================================================
# FONCTION 1 — Extraction de mots-clés via LLM
# ============================================================

def extract_keywords(transcript: str, max_keywords: int = 10) -> List[str]:
    """
    Extrait les mots-clés thématiques d'une transcription de podcast
    en utilisant GPT-4o-mini.

    Contrairement à la V1 (matching sur lexique fixe), le LLM comprend
    le sens global du discours et peut identifier des concepts
    non anticipés dans le dictionnaire éditorial.

    Args:
        transcript: Texte transcrit du podcast
        max_keywords: Nombre maximum de mots-clés à retourner

    Returns:
        Liste de mots-clés pertinents extraits par le LLM
    """
    if not transcript or len(transcript.strip()) < 50:
        return []

    # On tronque la transcription pour éviter de dépasser le context window
    # et maîtriser les coûts (4000 chars ≈ ~1000 tokens)
    transcript_excerpt = transcript[:4000]

    prompt = f"""Tu es un éditeur expert de la plateforme Inspiron, spécialisée dans 
la santé mentale et le bien-être au travail.

Voici la transcription d'un épisode de podcast :

---
{transcript_excerpt}
---

Extrait exactement {max_keywords} mots-clés ou expressions-clés thématiques 
qui résument le mieux le contenu de cet épisode.

Règles :
- Privilégie les concepts liés au bien-être, à la santé mentale, aux relations au travail
- Les mots-clés doivent être utiles pour indexer et retrouver cet épisode
- Mélange mots simples et expressions (2-3 mots max par expression)
- Réponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans explication
- Format attendu : {{"keywords": ["mot1", "expression 2", "mot3", ...]}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un assistant éditorial expert en bien-être au travail. "
                               "Tu réponds toujours en JSON valide, sans markdown ni explication.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.3,   # Faible température = réponses cohérentes et reproductibles
            max_tokens=300,
        )

        raw = response.choices[0].message.content.strip()

        # Parser le JSON retourné par le LLM
        data = json.loads(raw)
        keywords = data.get("keywords", [])

        # Sécurité : on s'assure que c'est bien une liste de strings
        keywords = [str(kw) for kw in keywords if kw]

        return keywords[:max_keywords]

    except json.JSONDecodeError:
        # Le LLM n'a pas retourné du JSON valide → fallback V1
        print("[nlp_v2] JSON invalide reçu du LLM → fallback V1")
        return extract_keywords_v1(transcript, max_keywords)

    except Exception as e:
        # Erreur API (quota, réseau, clé invalide...) → fallback V1
        print(f"[nlp_v2] Erreur API OpenAI : {e} → fallback V1")
        return extract_keywords_v1(transcript, max_keywords)


# ============================================================
# FONCTION 2 — Catégorisation via LLM
# ============================================================

def guess_category(transcript: str) -> str:
    """
    Identifie la catégorie éditoriale principale d'un épisode
    en utilisant GPT-4o-mini.

    Contrairement à la V1 (scoring par comptage de mots-clés),
    le LLM comprend le sens global du discours pour choisir
    la catégorie la plus pertinente, même si les mots exacts
    ne sont pas présents dans un lexique prédéfini.

    Args:
        transcript: Texte transcrit du podcast

    Returns:
        Une des trois catégories éditoriales Inspiron
    """
    if not transcript or len(transcript.strip()) < 50:
        return "Régulation intérieure et bien-être"

    transcript_excerpt = transcript[:4000]

    categories_str = "\n".join([f"- {c}" for c in CATEGORIES])

    prompt = f"""Tu es un éditeur expert de la plateforme Inspiron, spécialisée dans 
la santé mentale et le bien-être au travail.

Voici la transcription d'un épisode de podcast :

---
{transcript_excerpt}
---

Classe cet épisode dans UNE SEULE des trois catégories éditoriales suivantes :
{categories_str}

Définitions des catégories :
- "Régulation intérieure et bien-être" : episodes sur la gestion des émotions, 
  le stress, l'anxiété, le burnout, les pratiques de bien-être (méditation, sophrologie...)
- "Communication, relations et intelligence collective" : épisodes sur les relations 
  au travail, les conflits, le feedback, le management, la cohésion d'équipe
- "Inspiration, sens et transformation" : épisodes sur la quête de sens, la reconversion, 
  les valeurs, la transformation personnelle, le leadership inspirant

Réponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans explication.
Format attendu : {{"category": "nom exact de la catégorie"}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un assistant éditorial expert en bien-être au travail. "
                               "Tu réponds toujours en JSON valide, sans markdown ni explication.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,   # Très faible : on veut une réponse déterministe
            max_tokens=100,
        )

        raw = response.choices[0].message.content.strip()

        data = json.loads(raw)
        category = data.get("category", "").strip()

        # Vérifier que la catégorie retournée est bien dans notre liste
        if category in CATEGORIES:
            return category
        else:
            # Le LLM a retourné une catégorie non reconnue → fallback V1
            print(f"[nlp_v2] Catégorie inconnue '{category}' → fallback V1")
            return guess_category_v1(transcript)

    except json.JSONDecodeError:
        print("[nlp_v2] JSON invalide reçu du LLM → fallback V1")
        return guess_category_v1(transcript)

    except Exception as e:
        print(f"[nlp_v2] Erreur API OpenAI : {e} → fallback V1")
        return guess_category_v1(transcript)


# ============================================================
# FONCTION 3 — Mapping catégorie → pochette (inchangée)
# ============================================================

def map_category_to_cover(category: str) -> str:
    """
    Retourne le chemin public de la pochette associée à la catégorie.
    Identique à la V1 — cette logique ne nécessite pas de LLM.
    """
    filename = CATEGORY_TO_COVER.get(category)

    if not filename:
        filename = CATEGORY_TO_COVER["Régulation intérieure et bien-être"]

    return f"/covers/{filename}"


# ============================================================
# TEST LOCAL — à lancer directement : python nlp_v2.py
# ============================================================

if __name__ == "__main__":
    sample_transcript = """
    Aujourd'hui on parle d'un sujet dont on n'ose pas toujours parler au travail : 
    le syndrome de l'imposteur. Ce sentiment persistant de ne pas être légitime, 
    de ne pas mériter sa place, d'être sur le point d'être 'démasqué'. 
    Beaucoup de professionnels, y compris des managers très expérimentés, 
    vivent avec cette charge mentale invisible au quotidien. 
    Comment reconnaître les signaux ? Comment réguler cette anxiété de performance ?
    On explore ensemble des outils concrets : la pleine conscience, 
    l'auto-compassion, et la reconnexion à ses valeurs profondes.
    """

    print("=== TEST nlp_v2.py ===\n")

    print("📝 Extraction de mots-clés (LLM)...")
    keywords = extract_keywords(sample_transcript, max_keywords=8)
    print(f"Mots-clés : {keywords}\n")

    print("🧭 Catégorisation (LLM)...")
    category = guess_category(sample_transcript)
    print(f"Catégorie : {category}\n")

    print("🖼️ Pochette associée...")
    cover = map_category_to_cover(category)
    print(f"Pochette : {cover}\n")

    print("✅ Test terminé.")
