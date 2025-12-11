# Agent_ia_think_ai
Agent IA Inspiron — Automatisation de la production audio
L’Agent IA Inspiron est un système automatisé conçu pour aider l’équipe éditoriale à traiter les podcasts envoyés par les contributeurs.
Il analyse l’audio, génère une transcription, extrait des mots-clés pertinents, identifie la catégorie éditoriale et prépare la publication vers Symfony.

✨ Fonctionnalités principales
🔹 1. Pré-traitement audio
Ajout automatique d’un générique d’introduction

Nettoyage léger et concaténation

Analyse qualité (durée, bruit, loudness, peak…)

🔹 2. Analyse & accessibilité
Transcription complète via Whisper

Extraction métadonnées (durée, auteur, format…)

Vérification des critères qualité (OK / À revoir / Refusé)

🔹 3. Intelligence éditoriale
Génération automatique de mots-clés pertinents

Détection de la catégorie parmi :

Régulation intérieure et bien-être

Communication, relations et intelligence collective

Inspiration, sens et transformation

Attribution automatique d’une pochette graphique

Détection automatique du contributeur (nom, photo, bio)

🔹 4. Publication
Création d’un objet Episode structuré

Préparation à l’envoi vers le back-office Symfony

🚀 Lancer le projet
1. Installer les dépendances
pip install -r requirements.txt
2. Lancer l’API FastAPI
uvicorn main:app --reload
➡️ http://127.0.0.1:8000/docs

3. Lancer l’interface Streamlit
streamlit run app_streamlit.py
➡️ http://localhost:8501

📂 Structure rapide
services/
│ audio.py        # analyse audio + intro
│ stt.py          # transcription Whisper
│ nlp.py          # mots clés, catégories, pochettes
│ contributors.py # infos contributeurs
│ publish.py      # envoi vers Symfony
Pré-requis
Python 3.10+

pip + venv

FFmpeg installé pour traiter l’audio (Windows/Mac/Linux)

Contributeurs
Ce projet est développé pour Inspiron, dans une démarche d’innovation au service de la santé mentale et du bien-être au travail.

