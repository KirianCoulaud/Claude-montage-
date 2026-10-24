"""Edit decision list for the 10 km tier-list video (all source times in seconds)."""

FPS = 30
W, H = 1080, 1920

SOURCES = {
    "v1": "source/tier-list-10km-montage-v2-leger.mp4",  # part 1, already titled
    "p1": "source/suite-partie1.mov",                     # raw, seances 4 to 7
    "p2": "source/suite-partie2.mov",                     # raw, seance 8 + b-roll
}
# Gain (dB) applied to each source's voice so the raw parts match part 1
GAIN_DB = {"v1": 0.0, "p1": 5.8, "p2": 4.0}

# B-roll in p2: legs shot 22.5-35.5, landscape (road) 36.0-42.6
LEGS, ROAD = "p2", "p2"

# Pieces in order. Audio always comes from (src, a, b).
#   kind "cam"   -> same footage, slow push-in from `zoom` (static=True: no push)
#   kind "broll" -> footage from (vsrc, vt) instead, voice kept underneath
#   kind "card"  -> burned-in end-of-segment board of part 1 replaced by a kinetic
#                   text card on a blurred background taken from `bg`
#   kind "outro" -> silent-ish b-roll for the final recap board
# `titled`: raw footage that needs the TIER LIST title drawn on top
# `pill`: segment label shown under the title (raw parts only)
P = []


def cam(src, a, b, zoom=1.0, **kw):
    P.append(dict(src=src, a=a, b=b, kind="cam", zoom=zoom, **kw))


def broll(src, a, b, vt, vsrc="p2", **kw):
    P.append(dict(src=src, a=a, b=b, kind="broll", vsrc=vsrc, vt=vt, zoom=1.0, **kw))


def card(src, a, b, bg):
    P.append(dict(src=src, a=a, b=b, kind="card", bg=bg))


# ---------------------------------------------------------------- part 1
cam("v1", 0.95, 2.60, 1.12)          # intro hook
cam("v1", 2.60, 5.75)
cam("v1", 6.15, 8.30)                # presentation
cam("v1", 8.30, 10.55, 1.12)
cam("v1", 10.55, 12.40)
cam("v1", 12.40, 14.35, 1.15)
cam("v1", 15.35, 16.25, 1.12)        # 1. Allure 5 km (B)
cam("v1", 16.25, 18.10)
cam("v1", 18.10, 21.00, static=True)
cam("v1", 21.00, 23.35, 1.12)
cam("v1", 23.35, 24.90)
card("v1", 24.90, 27.35, bg=20.00)
cam("v1", 28.95, 32.15, 1.12)        # 2. Seuil SV2 (S)
cam("v1", 32.15, 35.20, static=True)
cam("v1", 35.20, 37.40, 1.12)
cam("v1", 37.40, 39.50)
card("v1", 39.50, 42.40, bg=35.00)
cam("v1", 44.10, 46.90, 1.12)        # 3. 10 km a fond (C)
cam("v1", 46.90, 47.90)
cam("v1", 47.90, 51.30, static=True)
cam("v1", 51.30, 53.47, 1.15)
card("v1", 53.47, 55.35, bg=49.50)

# ---------------------------------------------------------------- part 2
T = dict(titled=True)
pill = "Sortie longue  ·  + 1h30"    # 4. Sortie longue (A)
cam("p1", 0.25, 2.00, 1.12, pill=pill, **T)
cam("p1", 2.00, 3.40, pill=pill, **T)
cam("p1", 3.40, 6.00, static=True, pill=pill, **T)
broll("p1", 6.00, 7.75, vt=22.6, pill=pill, **T)
cam("p1", 7.75, 9.95, 1.12, pill=pill, **T)
pill = "Séances de côtes"            # 5. Cotes (B)
cam("p1", 10.25, 12.40, pill=pill, **T)
cam("p1", 12.40, 14.30, static=True, pill=pill, **T)
cam("p1", 14.30, 16.30, 1.12, pill=pill, **T)
cam("p1", 16.30, 18.65, pill=pill, **T)
broll("p1", 18.65, 20.75, vt=26.0, pill=pill, **T)
pill = "4 x 2000 m  ·  Allure 10 km"  # 6. 4 x 2000 (S)
cam("p1", 21.90, 23.70, 1.12, pill=pill, **T)
cam("p1", 23.70, 26.75, static=True, pill=pill, **T)
cam("p1", 26.75, 28.55, pill=pill, **T)
broll("p1", 28.55, 30.15, vt=36.4, pill=pill, **T)
pill = "Zone 3  ·  Tempo"            # 7. Zone 3 / tempo (C)
cam("p1", 30.40, 32.75, 1.12, pill=pill, **T)
cam("p1", 32.75, 33.75, pill=pill, **T)
# the verdict ("c'est pas ce qu'on aime, donc plutot rang C") is said at the end
# of the take: moved up so the board shows at the start of the seance
cam("p1", 38.60, 40.55, static=True, pill=pill, **T)
cam("p1", 34.25, 36.55, 1.12, pill=pill, **T)
broll("p1", 36.55, 38.40, vt=29.6, pill=pill, **T)
pill = "10 x 400 m  ·  VMA"          # 8. 10 x 400 (A)
cam("p2", 0.10, 1.80, 1.12, pill=pill, **T)
cam("p2", 1.80, 4.40, pill=pill, **T)
cam("p2", 4.40, 6.55, static=True, pill=pill, **T)
broll("p2", 6.55, 8.95, vt=31.0, pill=pill, **T)
cam("p2", 8.95, 11.65, 1.12, pill=pill, **T)
# final recap on the road shot (ambient sound of that shot)
P.append(dict(src="p2", a=37.00, b=40.40, kind="outro", zoom=1.0, titled=True))

PIECES = P

# Tier boards. Start/end/drop are (src, time) in source time.
BOARDS = [
    dict(a=("v1", 2.65), b=("v1", 4.75), card=None),  # blank board in the intro
    dict(a=("v1", 18.10), b=("v1", 21.00), drop=("v1", 19.27), card=("B", "Allure 5 km", "4 x 1000 m")),
    dict(a=("v1", 32.15), b=("v1", 35.20), drop=("v1", 33.14), card=("S", "Seuil SV2", "3 x 10 min")),
    dict(a=("v1", 47.90), b=("v1", 51.30), drop=("v1", 49.48), z=("v1", 50.84),
         card=("C", "10 km à fond", "à chaque sortie")),
    dict(a=("p1", 3.40), b=("p1", 6.00), drop=("p1", 4.23), card=("A", "Sortie longue", "+ 1h30")),
    dict(a=("p1", 12.40), b=("p1", 14.30), drop=("p1", 13.41), card=("B", "Côtes", "séances en côte")),
    dict(a=("p1", 23.70), b=("p1", 26.75), drop=("p1", 24.58), card=("S", "4 x 2000 m", "allure 10 km")),
    dict(a=("p1", 38.60), b=("p1", 35.00), drop=("p1", 40.00), card=("C", "Zone 3", "tempo")),
    dict(a=("p2", 4.40), b=("p2", 7.10), drop=("p2", 5.76), card=("A", "10 x 400 m", "VMA")),
    dict(a=("p2", 37.00), b=("p2", 40.40), card=None, recap=True),  # final, every card
]

# Corrected transcript: (src, start time, word). Timestamps from Parakeet TDT,
# text fixed by hand.
_v1 = [
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
_p1 = [
    (0.44, "Ensuite,"), (1.03, "on"), (1.11, "a"), (1.27, "les"), (1.43, "sorties"), (1.75, "longues"),
    (2.18, "au-dessus"), (2.50, "d'une"), (2.66, "heure"), (2.90, "et"), (2.98, "demie."),
    (3.51, "Ça,"), (3.67, "je"), (3.83, "le"), (3.91, "mets"), (4.07, "en"), (4.23, "A."),
    (4.80, "Très"), (4.96, "bonne"), (5.20, "sortie"), (5.72, "pour"), (5.96, "travailler"), (6.28, "sa"),
    (6.44, "durabilité"), (6.84, "en"), (7.00, "course"), (7.32, "à"), (7.48, "pied"),
    (7.80, "et"), (8.20, "pouvoir"), (8.60, "finir"), (8.76, "fort"), (9.00, "sur"), (9.08, "son"), (9.32, "10K."),
    (10.44, "Ensuite,"), (10.84, "on"), (11.00, "a"), (11.16, "les"), (11.32, "séances"), (11.56, "de"),
    (11.72, "côtes."), (12.53, "Donc"), (12.69, "ça,"), (12.85, "c'est"), (13.01, "plutôt"), (13.25, "en"),
    (13.41, "B."), (14.37, "Intéressant"), (14.85, "à"), (14.93, "placer"), (15.17, "dans"), (15.25, "sa"),
    (15.41, "prépa"), (15.75, "10K,"), (16.37, "mais"), (16.69, "souvent"), (16.93, "mal"), (17.17, "dosé"),
    (17.57, "et"), (17.73, "pas"), (17.97, "au"), (18.05, "bon"), (18.29, "moment."),
    (18.76, "Donc"), (18.92, "ça"), (19.08, "peut"), (19.16, "générer"), (19.48, "pas"), (19.64, "mal"),
    (19.72, "de"), (19.80, "fatigue"), (20.20, "nerveuse."),
    (22.10, "4"), (22.26, "x"), (22.42, "2000"), (22.74, "à"), (22.82, "l'allure"), (23.30, "10"),
    (23.46, "km,"), (23.86, "pour"), (23.94, "moi"), (24.02, "c'est"), (24.26, "rang"), (24.58, "S."),
    (25.28, "Une"), (25.52, "des"), (25.60, "meilleures"), (25.76, "séances"), (26.16, "pour"),
    (26.32, "travailler"), (26.87, "sur"), (27.03, "ses"), (27.27, "allures"), (27.75, "10"), (27.95, "km,"),
    (28.63, "et"), (28.71, "vraiment"), (28.87, "sur"), (29.03, "des"), (29.11, "séries"), (29.43, "longues."),
    (30.58, "Ensuite,"), (30.90, "on"), (30.98, "va"), (31.06, "avoir"), (31.22, "tout"), (31.30, "ce"),
    (31.38, "qui"), (31.54, "va"), (31.70, "être"), (31.86, "zone"), (32.10, "3,"),
    (32.87, "travail"), (33.35, "tempo."),
    (34.39, "Pas"), (34.63, "très"), (34.79, "intéressant"), (35.19, "sur"), (35.27, "des"), (35.43, "prépas"),
    (35.83, "10"), (35.99, "km,"), (36.80, "peut"), (37.04, "créer"), (37.36, "beaucoup"), (37.52, "de"),
    (37.60, "fatigue."),
    (38.74, "C'est"), (38.90, "pas"), (38.98, "ce"), (39.06, "qu'on"), (39.22, "aime,"), (39.46, "donc"),
    (39.62, "plutôt"), (39.86, "rang"), (40.00, "C."),
]
_p2 = [
    (0.24, "Ensuite,"), (0.64, "on"), (0.72, "va"), (0.80, "avoir"), (1.04, "la"), (1.12, "classique :"),
    (1.88, "10"), (2.04, "x"), (2.28, "400"), (2.92, "à"), (3.08, "VMA."),
    (4.48, "Séance"), (4.72, "que"), (4.88, "je"), (4.96, "placerais"), (5.44, "plutôt"), (5.60, "en"),
    (5.76, "A."), (6.63, "Pas"), (6.79, "mal"), (6.95, "en"), (7.03, "début"), (7.35, "de"),
    (7.43, "préparation"), (7.91, "pour"), (8.07, "faire"), (8.31, "vraiment"), (8.47, "de"), (8.55, "la"),
    (8.71, "vitesse,"), (9.52, "et"), (9.68, "se"), (9.84, "rassurer"), (10.24, "pour"), (10.40, "plus"),
    (10.48, "tard"), (10.64, "sur"), (10.72, "les"), (10.80, "allures"), (11.12, "10"), (11.28, "km."),
]
WORDS = [("v1", t, w) for t, w in _v1] + [("p1", t, w) for t, w in _p1] + [("p2", t, w) for t, w in _p2]

# Words emphasised in the subtitles / kinetic cards
HIGHLIGHT = {"pires", "meilleures", "Kirian.", "diplômé,", "B.", "S", "S.", "C,", "C.", "A.", "Z !",
             "vitesse.", "vitesse,", "SV2.", "seuil", "élevée.", "blesser", "performer.", "classer",
             "durabilité", "nerveuse.", "VMA.", "tempo."}


def _snap():
    # Align every cut on the 30 fps frame grid so audio and video stay in sync
    for p in PIECES:
        for k in ("a", "b", "bg", "vt"):
            if k in p:
                p[k] = round(p[k] * FPS) / FPS


_snap()


def new_time(src, t):
    """Map a source time to the edited timeline (None if it falls in a cut)."""
    acc = 0.0
    for p in PIECES:
        if p["src"] == src and p["a"] - 1e-6 <= t <= p["b"] + 1e-6:
            return acc + t - p["a"]
        acc += p["b"] - p["a"]
    return None


def piece_starts():
    out, acc = [], 0.0
    for p in PIECES:
        out.append(acc)
        acc += p["b"] - p["a"]
    return out, acc
