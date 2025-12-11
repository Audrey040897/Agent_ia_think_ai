import datetime
from pathlib import Path
from typing import Optional

import streamlit as st

from services import audio, stt, nlp
from models.episode import Episode


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_RAW_DIR = BASE_DIR / "uploads" / "raw"
UPLOAD_FINAL_DIR = BASE_DIR / "uploads" / "final"


def save_uploaded_file(file) -> Path:
    """Sauvegarde un fichier Streamlit dans uploads/raw/."""
    UPLOAD_RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = UPLOAD_RAW_DIR / file.name
    with open(dest, "wb") as f:
        f.write(file.getbuffer())
    return dest


def build_episode_from_file(
    file_path: Path,
    contributor_email: str,
    contributor_name: Optional[str] = None,
) -> Episode:
    """
    Pipeline complet local :
    - audio.build_final_audio
    - stt.transcribe
    - nlp.extract_keywords / guess_category / map_category_to_cover
    - construit un Episode
    """

    # 1. Audio final + qualité
    audio_info = audio.build_final_audio(str(file_path))

    # 2. Transcription
    transcript = stt.transcribe(audio_info["final_path"])

    # 3. NLP
    keywords = nlp.extract_keywords(transcript)
    category = nlp.guess_category(transcript)
    cover_image = nlp.map_category_to_cover(category)

    # 4. Episode (brouillon)
    title = "Titre provisoire"
    if contributor_name:
        title = f"{title} - {contributor_name}"

    episode = Episode(
        title=title,
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

    # On renvoie aussi info audio détaillée pour l'affichage
    return episode, audio_info


def main():
    st.set_page_config(
        page_title="Agent IA de publication Inspiron",
        layout="wide",
    )

    st.title("🎧 Agent IA de publication – Inspiron")
    st.markdown(
        """
        Cet agent prend en charge un épisode audio de A à Z :

        1. **Pré-traitement** : fichier, audio final, qualité éditoriale  
        2. **Analyse & accessibilité** : transcription Whisper complète  
        3. **Indexation intelligente** : mots-clés, catégorie, pochette  
        4. **Préparation à la publication** : épisode prêt pour Symfony  
        """
    )

    st.sidebar.header("⚙️ Paramètres contributeur")
    contributor_name = st.sidebar.text_input("Nom du contributeur", value="Contributeur·rice Inspiron")
    contributor_email = st.sidebar.text_input("Email du contributeur", value="test@inspiron.com")

    st.sidebar.markdown("---")
    st.sidebar.info("Charge un fichier audio ou vidéo (mp3, mp4, m4a, wav...)")

    uploaded_file = st.file_uploader(
        "Déposez un fichier audio/vidéo Inspiron",
        type=["mp3", "mp4", "m4a", "wav"],
    )

    if uploaded_file is not None:
        st.success(f"✅ Fichier reçu : **{uploaded_file.name}**")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        process_btn = st.button("🚀 Lancer le traitement complet", use_container_width=True)

    if process_btn:
        if uploaded_file is None:
            st.error("Merci d'importer un fichier avant de lancer le traitement.")
            return

        if not contributor_email:
            st.error("Merci de renseigner un email de contributeur.")
            return

        with st.spinner("Traitement en cours… (audio + transcription + indexation)"):
            raw_path = save_uploaded_file(uploaded_file)
            episode, audio_info = build_episode_from_file(
                file_path=raw_path,
                contributor_email=contributor_email,
                contributor_name=contributor_name,
            )

        st.success("✅ Traitement terminé !")

        # --- Mise en forme des résultats ---

        st.subheader("1️⃣ Pré-traitement & Qualité audio")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Infos fichier**")
            st.write(f"- Nom : `{Path(audio_info['final_path']).name}`")
            st.write(f"- Date de traitement : {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
            st.write(f"- Durée : {round(episode.duration / 60, 1)} minutes")

            if "quality_details" in audio_info:
                tech = audio_info["quality_details"]["tech"]
                st.markdown("**Format technique**")
                st.write(f"- Format : `{tech['suffix']}`")
                st.write(f"- Sample rate : {tech['sample_rate_hz']} Hz")
                st.write(f"- Bit depth : {tech['bit_depth']} bits")
                st.write(f"- Bitrate approx : {tech['bitrate_kbps_approx']} kbps")

        with col_b:
            st.markdown("**Qualité éditoriale**")
            quality_status = episode.quality_status
            quality_score = episode.quality_score

            if quality_status == "OK":
                st.success(f"Qualité : **{quality_status}** (score {quality_score}/100)")
            elif quality_status == "A_REVOIR":
                st.warning(f"Qualité : **{quality_status}** (score {quality_score}/100)")
            else:
                st.error(f"Qualité : **{quality_status}** (score {quality_score}/100)")

            if "quality_details" in audio_info:
                checks = audio_info["quality_details"]["checks"]
                with st.expander("Détails des critères éditoriaux"):
                    for name, info in checks.items():
                        ok = info.get("ok", False)
                        msg = info.get("message", "")
                        icon = "✅" if ok else "⚠️"
                        st.write(f"- {icon} **{name}** : {msg}")

        st.subheader("2️⃣ Analyse & accessibilité – Transcription")

        with st.expander("📄 Afficher la transcription complète"):
            st.text_area(
                "Transcription Whisper",
                value=episode.transcript,
                height=300,
            )

        # --- Indexation ---

        st.subheader("3️⃣ Indexation intelligente")

        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown("**Catégorie proposée**")
            st.write(f"🧭 {episode.category}")

            st.markdown("**Mots-clés**")
            if episode.keywords:
                st.write(", ".join(episode.keywords))
            else:
                st.write("_Aucun mot-clé détecté_")

        with col_d:
            st.markdown("**Pochette associée**")
            st.write(f"📦 `{episode.cover_image}` (mapping catégorie → pochette)")

        # --- Préparation publication ---

        st.subheader("4️⃣ Préparation à la publication (Symfony)")

        st.markdown(
            """
            L’épisode est prêt à être envoyé au back-office Symfony :
            - audio final
            - métadonnées
            - transcription
            - qualité
            - indexation
            """
        )

        # Payload simulé pour Symfony
        simulated_payload = {
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
            "status": episode.status,
        }

        with st.expander("Voir le payload JSON prêt pour Symfony"):
            st.json(simulated_payload)

        st.info(
            "➡️ Dans une version connectée, ce JSON serait envoyé automatiquement vers l’API Symfony "
            "pour créer l’épisode en brouillon."
        )


if __name__ == "__main__":
    main()
