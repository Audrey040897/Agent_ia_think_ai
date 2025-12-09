# main.py

from pydub import AudioSegment
import os

# --- Configuration ---
AUDIO_FILE = "data_in/test_podcast.m4a"
OUTPUT_DIR = "data_out"
THRESHOLD_LOW_VOLUME_DBFS = -35  # Exemple de seuil (valeur négative, plus c'est proche de 0, plus c'est fort)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def preprocess_audio(file_path):
    """
    Vérifie la qualité de base de l'audio et extrait les métadonnées simples.
    """
    print(f"--- 1. Début du pré-traitement pour {file_path} ---")
    
    try:
        # 1. Chargement du fichier
        audio = AudioSegment.from_file(file_path)
        
        # 2. Extraction des métadonnées
        duration_ms = len(audio)
        duration_sec = duration_ms / 1000
        print(f"Durée du podcast : {duration_sec:.2f} secondes.")
        
        # 3. Vérification de la qualité simple (Volume)
        average_volume = audio.dBFS # Mesure le volume moyen en décibels relatifs à la pleine échelle
        print(f"Volume moyen (dBFS) : {average_volume:.2f}")
        
        # 4. Production de la note de qualité
        note_qualite = "OK"
        if average_volume < THRESHOLD_LOW_VOLUME_DBFS:
            note_qualite = "À revoir"
            print("🚨 AVERTISSEMENT : Volume trop faible. Statut 'À revoir'.")
        
        # 5. Simulation de l'ajout des génériques (pour le scope MVP)
        # NOTE: L'ajout réel nécessiterait les fichiers génériques et une logique de mixage.
        # Pour le MVP, on se concentre sur les critères de vérification.
        
        return {
            "duration_sec": duration_sec,
            "average_volume": average_volume,
            "note_qualite": note_qualite
        }
        
    except Exception as e:
        print(f"Erreur lors du pré-traitement audio : {e}")
        return None

# --- Exécution du Pipeline ---
if __name__ == "__main__":
    metadata_audio = preprocess_audio(AUDIO_FILE)
    
    if metadata_audio:
        print("\n--- Résultat du Pré-traitement ---")
        print(metadata_audio)
    else:
        print("Le pipeline a échoué à l'étape du pré-traitement.")