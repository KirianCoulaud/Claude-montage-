# Montage – Tier list des séances 10 km

Résultat : `../tier-list-10km-final.mp4` (1080x1920, 30 fps, 1 min 38, -14 LUFS, ~97 Mo).
Export : `TARGET_MB=98 python3 render.py` (2 passes, juste sous 100 Mo) ou `HQ=1` (~185 Mo).

- Sources : `source/` (partie 1 déjà titrée + suite partie 1 et 2 brutes, plans jambes / route en fin de partie 2).
- `timeline.py` : découpe (blancs retirés), transcription corrigée mot à mot, moments où les tableaux apparaissent.
- `build_base.py` : coupe la source, zooms dynamiques, fonds flous des cartes texte → `build/base.mp4` + `build/voice.wav`.
- `render.py` : tableaux animés, sous-titres dynamiques, cartes texte, flashs, bruitages (`sfx.py`, sons synthétisés sans droits) et export final.

```
cd montage && python3 build_base.py && python3 render.py
```
Nécessite ffmpeg, numpy et Pillow. Les polices sont des Poppins (licence OFL).
