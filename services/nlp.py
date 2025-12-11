from typing import List, Dict
import re
from collections import Counter

# Stopwords FR très simples pour filtrer les mots sans intérêt
BASIC_STOPWORDS = {
    "je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
    "de", "du", "des", "le", "la", "les", "un", "une", "et",
    "à", "au", "aux", "en", "dans", "par", "pour", "sur",
    "ce", "cet", "cette", "ces", "ça", "cela", "comme",
    "qui", "que", "quoi", "dont", "où",
    "ne", "pas", "plus", "moins", "très", "trop",
    "est", "suis", "es", "sommes", "êtes", "sont",
    "ai", "as", "avons", "avez", "ont",
    "fait", "fais", "faisons", "faites",
    "avec", "sans",
    "on", "se", "sa", "son", "ses", "mon", "ma", "mes",
    "toi", "moi", "lui", "leur", "leurs",
    "y", "là",
}
# Vocabulaire éditorial Inspiron : mots-clés "officiels"
CURATED_KEYWORDS = [
    "santé mentale",
    "bien-être au travail",
    "stress",
    "anxiété",
    "charge mentale",
    "épuisement",
    "burnout",
    "burn-out",
    "bore-out",
    "fatigue émotionnelle",
    "fatigue compassionnelle",
    "hyper-adaptation",
    "sur-engagement",
    "signaux faibles",
    "prévention rps",
    "vulnérabilité",
    "résilience",
    "estime de soi",
    "confiance en soi",
    "syndrome de l’imposteur",
    "syndrome de l'imposteur",
    "culpabilité",
    "peur de l’échec",
    "peur de l'echec",
    "surmenage",
    "rumination",
    "lâcher-prise",
    "lacher-prise",
    "régulation émotionnelle",
    "regulation emotionnelle",
    "communication bienveillante",
    "communication non violente",
    "écoute active",
    "conflit au travail",
    "tensions d’équipe",
    "tensions d'equipe",
    "feedback",
    "reconnaissance",
    "soutien social",
    "cohésion d’équipe",
    "cohesion d'equipe",
    "intelligence collective",
    "confiance dans l’équipe",
    "confiance dans l'equipe",
    "coopération",
    "cooperation",
    "climat de travail",
    "violences symboliques",
    "micro-agressions",
    "microagressions",
    "harcèlement moral",
    "harcelement moral",
    "management toxique",
    "qualité du lien",
    "relations professionnelles",
    "qvct",
    "qualité de vie au travail",
    "qualite de vie au travail",
    "risques psychosociaux",
    "rps",
    "conditions de travail",
    "équilibre vie pro",
    "equilibre vie pro",
    "équilibre vie perso",
    "equilibre vie perso",
    "télétravail",
    "teletravail",
    "travail hybride",
    "surcharge de travail",
    "objectifs inatteignables",
    "hyper-connexion",
    "hyper connexion",
    "droit à la déconnexion",
    "droit a la deconnexion",
    "temps de repos",
    "charge invisible",
    "réunions toxiques",
    "reunions toxiques",
    "organisation du travail",
    "culture d’entreprise",
    "culture d'entreprise",
    "sens au travail",
    "transformations organisationnelles",
    "réorganisation",
    "reorganisation",
    "changement au travail",
    "managers",
    "leadership",
    "management bienveillant",
    "posture de dirigeant",
    "solitude du dirigeant",
    "indépendants",
    "independants",
    "freelances",
    "professions de l’accompagnement",
    "professions de l'accompagnement",
    "coachs",
    "thérapeutes",
    "therapeutes",
    "soignants",
    "aidants",
    "nouveaux managers",
    "prise de fonction",
    "gestion d’équipe",
    "gestion d'equipe",
    "responsabilité",
    "responsabilite",
    "quête de sens",
    "quete de sens",
    "réalignement",
    "realignement",
    "valeurs personnelles",
    "mission de vie",
    "transitions professionnelles",
    "reconversion",
    "crise de sens",
    "perte de motivation",
    "blues du dimanche soir",
    "désengagement",
    "desengagement",
    "ennui au travail",
    "créativité",
    "creativite",
    "intuition",
    "imagination",
    "inspiration",
    "antifragilité",
    "antifragilite",
    "transformation intérieure",
    "transformation interieure",
    "chemin de vie",
    "micro-pauses",
    "micro pauses",
    "respiration",
    "méditation",
    "meditation",
    "sophrologie",
    "ancrage",
    "pleine conscience",
    "auto-observation",
    "auto observation",
    "auto-diagnostic",
    "auto diagnostic",
    "routines de régulation",
    "hygiene mentale",
    "hygiène mentale",
    "auto-compassion",
    "auto compassion",
    "prise de recul",
    "décision consciente",
    "decision consciente",
    "priorisation",
    "limites saines",
    "assertivité",
    "assertivite",
    "deuil au travail",
    "maladie chronique",
    "handicap invisible",
    "charge familiale",
    "parentalité",
    "parentalite",
    "retour de congé maternité",
    "retour de conge maternite",
    "retour de congé paternité",
    "retour de conge paternite",
    "conflits de valeurs",
    "environnement toxique",
    "insécurité professionnelle",
    "insecurite professionnelle",
    "licenciement",
    "restructuration",
    "tensions hiérarchiques",
    "tensions hierarchiques",
]

# Dictionnaire de thèmes Inspiron : catégorie -> liste de mots/expressions associées
THEME_LEXICON: Dict[str, List[str]] = {
    "Burn-out & épuisement": [
        "burn out", "burn-out", "burnout",
        "épuisement", "épuisé", "fatigue chronique",
        "perte de sens", "surcharge", "charge mentale",
    ],
    "Télétravail & isolement": [
        "télétravail", "remote", "travail à distance",
        "isolement", "solitude", "zoom", "teams",
    ],
    "Conflits & relations": [
        "conflit", "tension", "désaccord",
        "communication", "feedback", "feedback difficile",
        "relation", "équipe", "collègue", "manager",
    ],
    "Motivation & engagement": [
        "motivation", "engagement", "démotivation",
        "procrastination", "objectifs", "sens du travail",
    ],
    "Stress & émotions": [
        "stress", "anxiété", "angoisse",
        "peur", "colère", "tristesse", "émotion",
        "régulation émotionnelle", "respiration",
    ],
    "Créativité & intuition": [
        "créativité", "créatif", "intuition",
        "idée", "innovation", "brainstorming",
    ],
    "Prévention RPS": [
        "risques psychosociaux", "rps",
        "harcèlement", "violence", "souffrance au travail",
        "pression", "charge de travail",
    ],
}


def _normalize(text: str) -> str:
    """Met en minuscules et retire les caractères exotiques."""
    text = text.lower()
    # Remplacer ponctuation par des espaces
    text = re.sub(r"[^\wàâäéèêëîïôöùûüç'-]+", " ", text, flags=re.UNICODE)
    return text


def _tokenize(text: str) -> List[str]:
    """Découpe en mots simples, en enlevant les stopwords et mots trop courts."""
    text = _normalize(text)
    tokens = text.split()
    tokens = [
        t.strip("'-")
        for t in tokens
        if len(t.strip("'-")) >= 3 and t not in BASIC_STOPWORDS
    ]
    return tokens

def extract_keywords(transcript: str, max_keywords: int = 10) -> List[str]:
    """
    Extracteur de mots-clés :
    1) repère les mots-clés éditoriaux CURATED_KEYWORDS présents dans le texte
    2) complète avec des mots fréquents significatifs
    """
    if not transcript:
        return []

    text_norm = _normalize(transcript)
    tokens = _tokenize(transcript)

    # 1) Mots-clés éditoriaux trouvés dans le texte
    curated_found = []
    for kw in CURATED_KEYWORDS:
        kw_norm = _normalize(kw)
        if kw_norm in text_norm:
            curated_found.append(kw)

    # 2) Mots fréquents "simples"
    counts = Counter(tokens)
    frequent = [w for w, _ in counts.most_common(30)]
    candidates = [
        w for w in frequent
        if len(w) >= 4 and w not in BASIC_STOPWORDS
    ]

    # 3) Fusion : d'abord les mots-clés éditoriaux, puis les mots fréquents
    merged = curated_found + candidates

    # 4) Supprimer les doublons en gardant l'ordre
    seen = set()
    unique_keywords: List[str] = []
    for w in merged:
        if w not in seen:
            seen.add(w)
            unique_keywords.append(w)

    # 5) Limiter à N mots-clés
    return unique_keywords[:max_keywords]

def guess_category(transcript: str) -> str:
    """
    Devine une catégorie principale en fonction des expressions trouvées
    dans le texte, à partir de THEME_LEXICON.
    """
    if not transcript:
        return "Bien-être général"

    text_norm = _normalize(transcript)
    scores = {}

    for category, expressions in THEME_LEXICON.items():
        score = 0
        for expr in expressions:
            if expr in text_norm:
                score += 1
        if score > 0:
            scores[category] = score

    if not scores:
        return "Bien-être général"

    # Catégorie avec le plus de "matchs"
    best_category = max(scores.items(), key=lambda x: x[1])[0]
    return best_category


def map_category_to_cover(category: str) -> str:
    """
    Associe une catégorie à une pochette par défaut.
    À adapter selon les assets graphiques d'Inspiron.
    """
    mapping = {
        "Burn-out & épuisement": "/covers/burnout.png",
        "Télétravail & isolement": "/covers/remote.png",
        "Conflits & relations": "/covers/conflicts.png",
        "Motivation & engagement": "/covers/motivation.png",
        "Stress & émotions": "/covers/stress.png",
        "Créativité & intuition": "/covers/creativity.png",
        "Prévention RPS": "/covers/rps.png",
        "Bien-être général": "/covers/general.png",
    }
    return mapping.get(category, "/covers/general.png")
from pathlib import Path

# ---------- Répertoires ----------
BASE_DIR = Path(__file__).resolve().parent.parent
COVERS_DIR = BASE_DIR / "resources" / "covers"

# ---------- Noms complets des catégories ----------
CATEGORY_REGULATION = "Régulation intérieure et bien-être"
CATEGORY_COMMUNICATION = "Communication, relations et intelligence collective"
CATEGORY_INSPIRATION = "Inspiration, sens et transformation"

# ---------- Mapping Catégorie → Pochette ----------
CATEGORY_TO_COVER = {
    CATEGORY_REGULATION: "Régulation intérieure et bien-être.png",
    CATEGORY_COMMUNICATION: "Communication, relations et intelligence collective.png",
    CATEGORY_INSPIRATION: "Inspiration, sens et transformation.png",
}

def map_category_to_cover(category: str) -> str:
    """
    Retourne le chemin public de la pochette associée à la catégorie.
    """
    filename = CATEGORY_TO_COVER.get(category)

    # Fallback : si catégorie inconnue, on choisit la catégorie régulation
    if not filename:
        filename = CATEGORY_TO_COVER[CATEGORY_REGULATION]

    # Chemin API (ton FastAPI doit servir /covers via StaticFiles)
    return f"/covers/{filename}"

