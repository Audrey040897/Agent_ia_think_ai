# Dictionnaire des contributeurs Inspiron
CONTRIBUTORS = {
    "stephanie.beaurain-ext@vertical-project.com": {
        "name": "Stéphanie Beaurain",
        "photo": "/contributors/stephanie_beaurain.jpg",   # optionnel
        "bio": "Contributrice Inspiron spécialiste bien-être et transformation.",  # optionnel
    },
    "valerie.jespere@gmail.com": {
        "name": "Valérie J'espère",
        "photo": "/contributors/valerie_jespere.jpg",
        "bio": "Coach et accompagnatrice en QVCT.",
    },
    "ericsalaun92@gmail.com": {
        "name": "Eric Salaun",
        "photo": "/contributors/eric_salaun.jpg",
        "bio": "Contributeur Inspiron spécialisé leadership et RPS.",
    },
    "gaelle.sophrocoach@gmail.com": {
        "name": "Gaëlle Piton",
        "photo": "/contributors/gaelle_piton.jpg",
        "bio": "Sophrologue et coach experte en régulation émotionnelle.",
    },
}
def get_contributor_info(email: str):
    """Retourne le profil du contributeur ou None s'il n'existe pas."""
    email = email.lower().strip()
    return CONTRIBUTORS.get(email)

