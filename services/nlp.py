def extract_keywords(text: str, top_n: int = 5):
    """
    Version simple : découpage par mots, fréquence,
    on garde les mots de longueur > 5.
    """
    tokens = [t.strip(".,!?;:()").lower() for t in text.split()]
    freq = {}
    for t in tokens:
        if len(t) > 5:
            freq[t] = freq.get(t, 0) + 1

    sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_tokens[:top_n]]


def guess_category(text: str) -> str:
    """
    Classe le podcast dans une catégorie simple en fonction de certains mots.
    """
    t = text.lower()
    if any(k in t for k in ["stress", "anxiété", "angoisse", "émotion", "respiration"]):
        return "Régulation émotionnelle"
    if any(k in t for k in ["conflit", "équipe", "manager", "hiérarchie", "communication"]):
        return "Relations au travail"
    if any(k in t for k in ["burn-out", "burnout", "épuisement", "charge mentale"]):
        return "Prévention RPS"
    return "Bien-être général"


def map_category_to_cover(category: str) -> str:
    """
    Associe une pochette à chaque catégorie.
    À adapter plus tard.
    """
    mapping = {
        "Régulation émotionnelle": "/covers/emotions.png",
        "Relations au travail": "/covers/relations.png",
        "Prévention RPS": "/covers/rps.png",
        "Bien-être général": "/covers/general.png",
    }
    return mapping.get(category, "/covers/general.png")
