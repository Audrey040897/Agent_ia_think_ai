# Agent_ia_think_ai
Agent IA Inspiron — Automatisation de la production audio

L'Agent IA Inspiron est un système automatisé conçu pour aider l'équipe éditoriale à traiter les podcasts envoyés par les contributeurs.
Il analyse l'audio, génère une transcription, extrait des mots-clés pertinents, identifie la catégorie éditoriale et prépare la publication vers Symfony.

---

## ✨ Fonctionnalités principales

### 🔹 1. Pré-traitement audio
- Ajout automatique d'un générique d'introduction
- Nettoyage léger et concaténation
- Analyse qualité (durée, bruit, loudness, peak…)

### 🔹 2. Analyse & accessibilité
- Transcription complète via Whisper
- Extraction métadonnées (durée, auteur, format…)
- Vérification des critères qualité (OK / À revoir / Refusé)

### 🔹 3. Intelligence éditoriale
- Génération automatique de mots-clés pertinents
- Détection de la catégorie parmi :
  - Régulation intérieure et bien-être
  - Communication, relations et intelligence collective
  - Inspiration, sens et transformation
- Attribution automatique d'une pochette graphique
- Détection automatique du contributeur (nom, photo, bio)

### 🔹 4. Publication
- Création d'un objet Episode structuré
- Préparation à l'envoi vers le back-office Symfony

---

## 🚀 Lancer le projet

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Configurer les variables d'environnement
```bash
cp .env.example .env
```
Ouvre `.env` et renseigne tes valeurs (voir section [Variables d'environnement](#-variables-denvironnement) ci-dessous).

### 3. Lancer l'API FastAPI
```bash
uvicorn main:app --reload
```
➡️ http://127.0.0.1:8000/docs

### 4. Lancer l'interface Streamlit
```bash
streamlit run app_streamlit.py
```
➡️ http://localhost:8501

---

## 📂 Structure du projet

```
Agent_ia_think_ai/
│
├── main.py                  # Point d'entrée API FastAPI
├── app_streamlit.py         # Interface utilisateur Streamlit
├── docker-compose.yml       # Déploiement Docker
├── requirements.txt         # Dépendances Python
├── .env.example             # Modèle de configuration (à copier en .env)
│
├── services/
│   ├── audio.py             # Analyse audio + ajout générique
│   ├── stt.py               # Transcription Whisper
│   ├── nlp.py               # V1 — mots-clés, catégories, pochettes (règles)
│   ├── nlp_v2.py            # V2 — mots-clés, catégories via LLM GPT-4o-mini
│   ├── contributors.py      # Infos contributeurs
│   └── publish.py           # Envoi vers Symfony
│
├── models/
│   └── episode.py           # Modèle de données Episode
│
├── uploads/
│   ├── raw/                 # Fichiers audio bruts déposés
│   └── final/               # Fichiers audio finaux (avec générique)
│
└── resources/
    ├── intro.mp3            # Générique d'introduction
    └── covers/              # Pochettes graphiques par catégorie
```

---

## 🔐 Variables d'environnement

Le projet utilise un fichier `.env` pour stocker les configurations sensibles.
**Ce fichier ne doit jamais être pushé sur GitHub** — il est ignoré via `.gitignore`.

Pour configurer ton environnement :
```bash
cp .env.example .env
```

Puis renseigne tes valeurs dans `.env` :

| Variable | Description | Obligatoire |
|---|---|---|
| `OPENAI_API_KEY` | Clé API OpenAI pour le module nlp_v2 (LLM) | ✅ Pour la V2 |
| `SYMFONY_API_URL` | URL de l'API Symfony pour la publication | ⚠️ Si publication active |
| `SYMFONY_API_TOKEN` | Token d'authentification Symfony | ⚠️ Si publication active |

> 🔑 Obtiens ta clé OpenAI sur : https://platform.openai.com/api-keys

---

## 🧠 Intelligence éditoriale V2 — LLM

### Pourquoi une V2 ?

La V1 (`nlp.py`) reposait sur un lexique de 150+ mots-clés prédéfinis.
Elle présentait deux limites :
- **Rigidité** : un terme absent du lexique était ignoré, même s'il était pertinent
- **Catégorisation approximative** : le scoring par comptage ne comprenait pas le sens global

La V2 (`nlp_v2.py`) remplace ces deux fonctions par des appels à **GPT-4o-mini**
pour une compréhension sémantique réelle du contenu.

### Comparaison V1 vs V2

| | V1 — NLP classique | V2 — LLM GPT-4o-mini |
|---|---|---|
| Extraction mots-clés | Matching sur lexique fixe | Compréhension sémantique |
| Catégorisation | Scoring par comptage | Compréhension du discours global |
| Généralisation | Limitée au lexique prévu | Généralise sur tout vocabulaire |
| Dépendance externe | Aucune | API OpenAI (~0.01€/appel) |
| Fallback | — | Retour automatique sur V1 si erreur API |

### Exemple de résultat

Sur le même texte parlant du syndrome de l'imposteur :

**V1 retournait :** `anxiété`, `managers`, `d'être`, `comment` ❌

**V2 retourne :** `syndrome de l'imposteur`, `anxiété de performance`, `légitimité au travail`, `auto-compassion` ✅

### Tester la V2

```bash
# Depuis la racine du projet
python -m services.nlp_v2
```

### Activer la V2 dans le pipeline

Dans `main.py` et `app_streamlit.py`, remplace :
```python
# V1 (actuel)
from services.nlp import extract_keywords, guess_category, map_category_to_cover

# V2 (LLM)
from services.nlp_v2 import extract_keywords, guess_category, map_category_to_cover
```

### Coûts estimés

| Usage | Coût estimé |
|---|---|
| 1 épisode traité | ~0.01€ |
| 100 épisodes | ~1€ |
| 1 000 épisodes | ~10€ |

### Gestion des erreurs

Le module V2 ne fait jamais tomber le pipeline :

| Situation | Comportement |
|---|---|
| Clé API invalide | Fallback automatique sur V1 |
| Quota dépassé | Fallback automatique sur V1 |
| Réponse JSON invalide | Fallback automatique sur V1 |
| Erreur réseau | Fallback automatique sur V1 |

---

## 🐳 Déploiement en production

### 1. Pré-requis
- Windows 11 (ou Mac/Linux)
- Docker Desktop installé et démarré (WSL2 activé sur Windows)
- Git

### 2. Récupérer le projet
```bash
git clone <repo>
cd Agent_ia_think_ai
```

### 3. Configurer l'environnement
```bash
cp .env.example .env
# Renseigne tes clés dans .env
```

### 4. Lancer en 1 commande
```bash
docker compose up --build
```
> Premier lancement = téléchargement des images et dépendances

### 5. Accéder à l'agent
- UI Streamlit → http://localhost:8501
- API FastAPI → http://localhost:8000/docs

### 6. Workflow
Déposer un fichier audio dans l'UI → lancer le traitement → vérifier les résultats → publier (si connecté au back Symfony)

### 7. Stopper
```bash
Ctrl + C
```

### 8. Relancer rapidement
```bash
docker compose up              # avec rebuild si nécessaire
docker compose up -d           # en arrière-plan
```

### 9. Logs & debug
```bash
docker compose logs -f
docker compose logs api -f
docker compose logs ui -f
```

### 10. Nettoyer
```bash
docker compose down                          # stopper et supprimer les conteneurs
docker compose down -v && docker system prune -af   # nettoyage complet
```

### 11. Mise à jour du code
```bash
git pull
docker compose up --build
```

### 12. Dépannage rapide

| Problème | Solution |
|---|---|
| Ports occupés | Changer `8000:8000` / `8501:8501` dans `docker-compose.yml` |
| Espace disque insuffisant | Nettoyer via Docker Desktop ou `docker system prune -af` |
| Clé API non reconnue | Vérifier le contenu de `.env` (pas d'espace, pas de guillemets) |

---

## 🧰 Pré-requis (hors Docker)

- Python 3.10+
- pip + venv
- FFmpeg installé ([Windows](https://ffmpeg.org/download.html) / Mac : `brew install ffmpeg` / Linux : `apt install ffmpeg`)

---

## 👥 Contributeurs

Ce projet est développé pour **Inspiron**, dans une démarche d'innovation
au service de la santé mentale et du bien-être au travail.