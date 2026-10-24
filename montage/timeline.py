"""Edit decision list for the 10 km tier-list video (all source times in seconds)."""

SRC = "source/tier-list-10km-montage-v2-leger.mp4"
FPS = 30
W, H = 1080, 1920

# Pieces kept from the source, in order: (src_start, src_end, kind, zoom)
#   kind "cam"  -> camera footage, zoom pushes slowly from `zoom`
#   kind "card" -> old burned-in tier board replaced by a kinetic text card on a
#                  blurred background taken from `bg` (src start)
PIECES = [
    # Intro hook
    dict(a=0.95, b=2.60, kind="cam", zoom=1.12),
    dict(a=2.60, b=5.75, kind="cam", zoom=1.00),
    # Presentation
    dict(a=6.15, b=8.30, kind="cam", zoom=1.00),
    dict(a=8.30, b=10.55, kind="cam", zoom=1.12),
    dict(a=10.55, b=12.40, kind="cam", zoom=1.00),
    dict(a=12.40, b=14.35, kind="cam", zoom=1.15),
    # Seance 1 - Allure 5 km (B)
    dict(a=15.35, b=16.25, kind="cam", zoom=1.12),
    dict(a=16.25, b=18.10, kind="cam", zoom=1.00),
    dict(a=18.10, b=21.00, kind="cam", zoom=1.00, static=True),
    dict(a=21.00, b=23.35, kind="cam", zoom=1.12),
    dict(a=23.35, b=24.90, kind="cam", zoom=1.00),
    dict(a=24.90, b=27.35, kind="card", bg=20.00),
    # Seance 2 - Seuil SV2 (S)
    dict(a=28.95, b=32.15, kind="cam", zoom=1.12),
    dict(a=32.15, b=35.20, kind="cam", zoom=1.00, static=True),
    dict(a=35.20, b=37.40, kind="cam", zoom=1.12),
    dict(a=37.40, b=39.50, kind="cam", zoom=1.00),
    dict(a=39.50, b=42.40, kind="card", bg=35.00),
    # Seance 3 - 10 km a fond (C)
    dict(a=44.10, b=46.90, kind="cam", zoom=1.12),
    dict(a=46.90, b=47.90, kind="cam", zoom=1.00),
    dict(a=47.90, b=51.30, kind="cam", zoom=1.00, static=True),
    dict(a=51.30, b=53.47, kind="cam", zoom=1.15),
    dict(a=53.47, b=55.35, kind="card", bg=49.50),
    # Final recap: the completed board from the source
    dict(a=55.35, b=56.90, kind="cam", zoom=1.00, static=True, recap=True),
]

# Tier boards, in source time. `drop` = when the card lands in its row.
BOARDS = [
    dict(a=2.65, b=4.75, card=None),  # blank board in the intro
    dict(a=18.10, b=21.00, drop=19.27, card=("B", "Allure 5 km", "4 x 1000 m")),
    dict(a=32.15, b=35.20, drop=33.14, card=("S", "Seuil SV2", "3 x 10 min")),
    dict(a=47.90, b=51.30, drop=49.48, card=("C", "10 km à fond", "à chaque sortie"), z=50.84),
]

# Corrected transcript with word start times (source time), from Parakeet TDT
# timestamps, text fixed by hand.
WORDS = [
    (1.16, "Aujourd'hui,"), (1.64, "on"), (1.80, "va"), (2.04, "classer"),
    (2.68, "les"), (3.00, "meilleures"), (3.24, "séances"), (3.64, "et"), (3.80, "les"),
    (3.96, "pires"), (4.28, "pour"), (4.44, "préparer"), (4.92, "son"), (5.16, "10"), (5.40, "km."),
    (6.32, "Déjà,"), (6.72, "salut,"), (7.04, "moi"), (7.20, "c'est"), (7.36, "Kirian."),
    (8.37, "Je"), (8.45, "suis"), (8.53, "coach"), (8.95, "sportif"), (9.41, "diplômé,"),
    (10.60, "spécialisé"), (11.16, "dans"), (11.40, "la"), (11.52, "course"), (11.75, "à"), (11.88, "pied."),
    (12.44, "Et"), (12.60, "aujourd'hui,"), (12.92, "on"), (13.08, "note"), (13.40, "les"),
    (13.48, "séances"), (13.80, "10"), (14.04, "km."),
    (15.57, "Première"), (15.89, "séance :"),
    (16.31, "4"), (16.55, "x"), (16.79, "1000"), (17.03, "à"), (17.11, "l'allure"), (17.51, "5"), (17.67, "km."),
    (18.23, "Celle-là,"), (18.55, "on"), (18.71, "va"), (18.79, "la"), (18.95, "mettre"), (19.11, "en"), (19.27, "B."),
    (19.99, "C'est"), (20.15, "une"), (20.31, "séance"), (20.55, "qui"), (20.71, "peut"), (21.03, "tout"),
    (21.19, "à"), (21.27, "fait"), (21.43, "s'inscrire"), (21.91, "dans"), (22.07, "un"), (22.23, "plan"),
    (22.55, "10"), (22.79, "km,"), (23.43, "surtout"), (23.67, "en"), (23.83, "début"), (24.15, "de"),
    (24.23, "prépa,"), (24.71, "dans"), (24.87, "l'objectif"), (25.43, "d'aller"), (25.75, "chercher"),
    (26.23, "un"), (26.31, "petit"), (26.47, "peu"), (26.63, "de"), (26.79, "vitesse."),
    (29.14, "Ensuite,"), (29.78, "on"), (29.94, "a"), (30.10, "un"), (30.26, "3"), (30.50, "x"),
    (30.74, "10"), (30.98, "minutes"), (31.30, "à"), (31.54, "SV2."),
    (32.26, "Celle-là,"), (32.58, "je"), (32.66, "la"), (32.82, "mets"), (32.98, "en"), (33.14, "S"),
    (33.62, "parce"), (33.78, "que"), (33.86, "c'est"), (34.02, "une"), (34.18, "séance"), (34.50, "qui"),
    (34.58, "va"), (34.74, "vraiment"), (34.90, "repousser"), (35.46, "son"), (35.62, "seuil"), (35.94, "2"),
    (36.50, "et"), (36.74, "nous"), (36.82, "permettre"), (37.14, "de"), (37.22, "vraiment"), (37.46, "tenir"),
    (37.70, "des"), (37.86, "allures"), (38.42, "à"), (38.50, "une"), (38.66, "vitesse"), (38.98, "élevée."),
    (39.46, "Et"), (39.54, "c'est"), (39.70, "vraiment"), (39.86, "ce"), (40.02, "qui"), (40.18, "manque"),
    (40.50, "parfois"), (40.98, "aux"), (41.14, "coureurs"), (41.54, "de"), (41.70, "10"), (41.94, "km."),
    (44.28, "Ensuite,"), (44.68, "on"), (44.76, "a"), (44.92, "la"), (45.00, "classique :"),
    (45.56, "vouloir"), (45.96, "courir"), (46.28, "un"), (46.36, "10"), (46.52, "km"), (46.92, "à"),
    (47.00, "fond"), (47.32, "à"), (47.40, "chaque"), (47.56, "sortie."),
    (48.04, "Celle-là,"), (48.44, "je"), (48.60, "la"), (48.68, "mets"), (48.92, "littéralement"),
    (49.32, "en"), (49.48, "C,"), (49.80, "on"), (50.04, "va"), (50.20, "même"), (50.44, "la"),
    (50.52, "mettre"), (50.68, "en"), (50.84, "Z !"),
    (51.40, "C'est"), (51.64, "la"), (51.80, "pire"), (52.12, "chose"), (52.44, "possible"),
    (52.92, "pour"), (53.24, "se"), (53.56, "blesser"), (54.20, "et"), (54.36, "ne"), (54.52, "pas"),
    (54.76, "performer."),
]

# Words emphasised in the subtitles / kinetic cards
HIGHLIGHT = {"pires", "meilleures", "Kirian.", "diplômé,", "B.", "S", "C,", "Z !", "vitesse.",
             "SV2.", "seuil", "élevée.", "blesser", "performer.", "classer", "4", "1000", "3", "10"}


def _snap():
    # Align every cut on the 30 fps frame grid so audio and video stay in sync
    for p in PIECES:
        for k in ("a", "b", "bg"):
            if k in p:
                p[k] = round(p[k] * FPS) / FPS


_snap()


def new_time(src_t):
    """Map a source time to the edited timeline (None if it falls in a cut)."""
    acc = 0.0
    for p in PIECES:
        if p["a"] - 1e-6 <= src_t <= p["b"] + 1e-6:
            return acc + src_t - p["a"]
        acc += p["b"] - p["a"]
    return None


def piece_starts():
    out, acc = [], 0.0
    for p in PIECES:
        out.append(acc)
        acc += p["b"] - p["a"]
    return out, acc
