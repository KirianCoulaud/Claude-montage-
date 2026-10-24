"""Step 2: draw every overlay (tier boards, kinetic cards, dynamic subtitles, flashes)
frame by frame with Pillow, composite on build/base.mp4, add the sound design and
export the final video."""
import math
import subprocess
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import sfx
from timeline import PIECES, BOARDS, WORDS, HIGHLIGHT, FPS, W, H, new_time, piece_starts

OUT = sys.argv[1] if len(sys.argv) > 1 else "../tier-list-10km-final.mp4"
FONT_DIR = "fonts/"
_fonts = {}


def font(name, size):
    key = (name, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(f"{FONT_DIR}Poppins-{name}.ttf", size)
    return _fonts[key]


TIER_COLORS = {"S": (245, 176, 0), "A": (40, 167, 69), "B": (255, 138, 28), "C": (240, 58, 30)}
TIERS = "SABC"
YELLOW = (255, 225, 77)


def ease_out_back(x, s=1.7):
    x = min(max(x, 0.0), 1.0) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def clamp01(x):
    return min(max(x, 0.0), 1.0)


# ----------------------------------------------------------------- timeline
STARTS, TOTAL = piece_starts()
NFRAMES = round(TOTAL * FPS)
boards = []
for b in BOARDS:
    nb = dict(b)
    nb["a"], nb["b"] = new_time(b["a"]), new_time(b["b"])
    if "drop" in b:
        nb["drop"] = new_time(b["drop"])
    if "z" in b:
        nb["z"] = new_time(b["z"])
    boards.append(nb)

cards = []  # kinetic text cards replacing the old end-of-segment boards
CARD_CONTEXT = [24.71, 39.46, 51.40]  # sentence start shown when the card opens
CARD_TIER = ["B", "S", "C"]
ci = 0
for i, p in enumerate(PIECES):
    if p["kind"] == "card":
        t0, t1 = STARTS[i], STARTS[i] + p["b"] - p["a"]
        ws = [(new_time(s) if s >= p["a"] - 0.05 else None, w) for s, w in WORDS
              if CARD_CONTEXT[ci] - 0.01 <= s < p["b"]]
        cards.append(dict(a=t0, b=t1, words=ws, tier=CARD_TIER[ci]))
        ci += 1

FLASH_AT = [STARTS[i] for i in (2, 6, 12, 17, 22)] + [c["a"] for c in cards]
RECAP_AT = STARTS[-1]


def in_card(t):
    return any(c["a"] <= t < c["b"] for c in cards)


# ------------------------------------------------------------- subtitles
def build_chunks():
    items = [(new_time(s), w) for s, w in WORDS]
    chunks, cur = [], []
    for i, (t, w) in enumerate(items):
        if in_card(t):
            continue
        if cur:
            prev_t, prev_w = cur[-1]
            text_len = sum(len(x) for _, x in cur) + len(w)
            if (len(cur) >= 3 or text_len > 16 or prev_w[-1] in ",.:!?" or t - prev_t > 0.45):
                chunks.append(cur)
                cur = []
        cur.append((t, w))
    if cur:
        chunks.append(cur)
    out = []
    for k, c in enumerate(chunks):
        start = c[0][0] - 0.03
        end = c[-1][0] + 0.55
        if k + 1 < len(chunks):
            end = min(end, chunks[k + 1][0][0] - 0.03)
        for cd in cards:  # never overlap a kinetic card
            if start < cd["a"] < end:
                end = cd["a"]
        out.append(dict(a=start, b=end, words=c))
    return out


CHUNKS = build_chunks()
_sub_cache = {}


def render_chunk(ch, active):
    key = (id(ch), active)
    if key in _sub_cache:
        return _sub_cache[key]
    size, stroke = 82, 9
    words = [w.upper() for _, w in ch["words"]]
    imgs = []
    for j, w in enumerate(words):
        is_act = j == active
        fs = int(size * (1.12 if is_act else 1.0))
        f = font("Black", fs)
        bbox = f.getbbox(w, stroke_width=stroke)
        im = Image.new("RGBA", (bbox[2] - bbox[0] + 8, int(size * 1.6)), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        color = YELLOW if is_act else (255, 255, 255)
        y = int(size * 1.6) // 2
        # soft drop shadow
        d.text((4 - bbox[0], y + 7), w, font=f, fill=(0, 0, 0, 140), anchor="lm",
               stroke_width=stroke, stroke_fill=(0, 0, 0, 140))
        d.text((-bbox[0], y), w, font=f, fill=color, anchor="lm",
               stroke_width=stroke, stroke_fill=(0, 0, 0))
        imgs.append(im)
    gap = 22
    lines, line, lw = [], [], 0
    for im in imgs:
        if line and lw + gap + im.width > 980:
            lines.append(line)
            line, lw = [], 0
        lw += (gap if line else 0) + im.width
        line.append(im)
    lines.append(line)
    lh = int(size * 1.15)
    canvas = Image.new("RGBA", (1040, lh * len(lines) + int(size * 0.5)), (0, 0, 0, 0))
    for li, ln in enumerate(lines):
        tw = sum(i.width for i in ln) + gap * (len(ln) - 1)
        x = (canvas.width - tw) // 2
        for im in ln:
            canvas.alpha_composite(im, (x, li * lh))
            x += im.width + gap
    _sub_cache[key] = canvas
    return canvas


def draw_subtitles(frame, t, board_on):
    for ch in CHUNKS:
        if ch["a"] <= t < ch["b"]:
            active = max(j for j, (wt, _) in enumerate(ch["words"]) if wt - 0.03 <= t or j == 0)
            img = render_chunk(ch, active)
            k = (t - ch["a"]) / 0.13
            sc = 0.55 + 0.45 * ease_out_back(k, 2.4) if k < 1 else 1.0
            if sc != 1.0:
                img = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))),
                                 Image.BILINEAR)
            cy = 1640 if board_on else 1360
            frame.alpha_composite(img, ((W - img.width) // 2, cy - img.height // 2))
            return


# ------------------------------------------------------------- tier board
ROW_Y0, ROW_STEP, ROW_H = 450, 250, 225
BADGE_X, BADGE_W = 50, 160
SLOT_X0, SLOT_X1 = 228, 1030


def make_row(tier):
    im = Image.new("RGBA", (SLOT_X1 + 10, ROW_H + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = TIER_COLORS[tier]
    d.rounded_rectangle((SLOT_X0, 2, SLOT_X1, ROW_H), 22, fill=(0, 0, 0, 55),
                        outline=c + (150,), width=3)
    d.rounded_rectangle((BADGE_X + 3, 8, BADGE_X + BADGE_W + 3, ROW_H + 6), 24, fill=(0, 0, 0, 110))
    d.rounded_rectangle((BADGE_X, 2, BADGE_X + BADGE_W, ROW_H), 24, fill=c + (255,))
    f = font("Black", 118)
    cx, cy = BADGE_X + BADGE_W // 2, ROW_H // 2 + 6
    d.text((cx + 5, cy + 6), tier, font=f, anchor="mm", fill=(40, 20, 0, 170))
    d.text((cx, cy), tier, font=f, anchor="mm", fill=(255, 255, 255), stroke_width=3,
           stroke_fill=(60, 30, 0))
    return im


def make_card(tier, title, sub):
    cw, chh = 392, 220
    im = Image.new("RGBA", (cw + 40, chh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = TIER_COLORS[tier]
    d.rounded_rectangle((26, 28, cw + 26, chh + 28), 24, fill=(0, 0, 0, 120))
    d.rounded_rectangle((20, 20, cw + 20, chh + 20), 24, fill=(14, 14, 16, 240), outline=c, width=5)
    d.text((20 + cw // 2, 20 + chh // 2 - 26), title, font=font("Bold", 46), anchor="mm",
           fill=(255, 255, 255))
    d.text((20 + cw // 2, 20 + chh // 2 + 32), sub, font=font("Medium", 34), anchor="mm",
           fill=(225, 225, 225))
    return im


ROWS = {t: make_row(t) for t in TIERS}
CARD_IMGS = {b["card"][0]: make_card(*b["card"]) for b in BOARDS if b["card"]}
CARD_POS_X = 608  # card left (incl. 20 px shadow margin)


def darken_layer(alpha):
    a = np.zeros((H, W), np.float32)
    a[440:] = 1.0
    ramp = np.linspace(0, 1, 440 - 340)
    a[340:440] = ramp[:, None]
    lay = np.zeros((H, W, 4), np.uint8)
    lay[..., 3] = (a * alpha * 255).astype(np.uint8)
    return Image.fromarray(lay, "RGBA")


DARK = darken_layer(0.5)


def draw_board(frame, t, b, idx):
    dur_in, dur_out = 0.32, 0.2
    a, e = b["a"], b["b"]
    fade = clamp01((t - a) / 0.2) * clamp01((e - t) / dur_out)
    # darkening of the footage under the board
    if fade < 1:
        dk = DARK.copy()
        dk.putalpha(dk.getchannel("A").point(lambda v: int(v * fade)))
        frame.alpha_composite(dk)
    else:
        frame.alpha_composite(DARK)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shake = 0
    if "drop" in b and 0 <= t - b["drop"] < 0.25:
        k = (t - b["drop"]) / 0.25
        shake = int(10 * (1 - k) * math.sin(k * 40))
    for i, tier in enumerate(TIERS):
        k = (t - a - i * 0.05) / dur_in
        x_off = int(-160 * (1 - ease_out_back(k))) if k < 1 else 0
        x_off -= int(80 * (1 - clamp01((e - t) / dur_out)))
        al = clamp01(k * 1.6) * clamp01((e - t) / dur_out)
        if al <= 0:
            continue
        row = ROWS[tier]
        if al < 1:
            row = row.copy()
            row.putalpha(row.getchannel("A").point(lambda v: int(v * al)))
        layer.alpha_composite(row, (max(0, x_off), ROW_Y0 + i * ROW_STEP + shake))

        # cards already placed on previous boards
        for pb in boards[1:idx]:
            if pb["card"][0] == tier:
                cimg = CARD_IMGS[tier]
                if al < 1:
                    cimg = cimg.copy()
                    cimg.putalpha(cimg.getchannel("A").point(lambda v: int(v * al)))
                layer.alpha_composite(cimg, (CARD_POS_X + max(0, x_off), ROW_Y0 + i * ROW_STEP - 18 + shake))

    if b["card"]:
        tier = b["card"][0]
        i = TIERS.index(tier)
        ty = ROW_Y0 + i * ROW_STEP - 18
        k = (t - (b["drop"] - 0.22)) / 0.22
        if k >= 0:
            land = ease_out(k)
            sc = 1.45 - 0.45 * land if k < 1 else 1.0
            y = int(ty - 340 * (1 - land))
            cimg = CARD_IMGS[tier]
            out_a = clamp01((e - t) / dur_out)
            if sc != 1.0:
                cimg = cimg.resize((int(cimg.width * sc), int(cimg.height * sc)), Image.BILINEAR)
            al = clamp01(k * 2) * out_a
            if al < 1:
                cimg = cimg.copy()
                cimg.putalpha(cimg.getchannel("A").point(lambda v: int(v * al)))
            cx = CARD_POS_X + 216 - cimg.width // 2
            cy = y + 130 - cimg.height // 2
            layer.alpha_composite(cimg, (cx, cy + shake))
            # glow flash on the row at landing
            g = t - b["drop"]
            if 0 <= g < 0.3:
                gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(gl).rounded_rectangle(
                    (SLOT_X0 - 6, ROW_Y0 + i * ROW_STEP - 6, SLOT_X1 + 6, ROW_Y0 + i * ROW_STEP + ROW_H + 6),
                    26, outline=TIER_COLORS[tier] + (int(255 * (1 - g / 0.3)),), width=10)
                layer.alpha_composite(gl)

    # "on va même la mettre en Z" stamp
    if "z" in b and t >= b["z"]:
        k = (t - b["z"]) / 0.18
        sc = 2.2 - 1.2 * ease_out_back(k, 2.0) if k < 1 else 1.0
        al = clamp01(k * 2) * clamp01((e - t) / dur_out)
        st = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
        d = ImageDraw.Draw(st)
        d.text((150, 160), "Z", font=font("Black", 210), anchor="mm", fill=(255, 40, 40),
               stroke_width=8, stroke_fill=(255, 255, 255))
        st = st.rotate(-14, resample=Image.BICUBIC)
        st = st.resize((int(300 * sc), int(300 * sc)), Image.BILINEAR)
        if al < 1:
            st.putalpha(st.getchannel("A").point(lambda v: int(v * al)))
        cy = ROW_Y0 + 3 * ROW_STEP + ROW_H // 2
        layer.alpha_composite(st, (410 - st.width // 2, cy - st.height // 2))

    frame.alpha_composite(layer)


# ------------------------------------------------------------- kinetic cards
_card_layout = {}


def layout_card(c):
    if id(c) in _card_layout:
        return _card_layout[id(c)]
    size = 104
    f = font("Black", size)
    gap, maxw, lh = 26, 960, int(size * 1.18)
    placed, x, line = [], 0, 0
    for t, w in c["words"]:
        txt = w.upper()
        bw = f.getbbox(txt, stroke_width=8)[2]
        if x and x + gap + bw > maxw:
            line += 1
            x = 0
        placed.append(dict(t=t, txt=txt, x=x + (gap if x else 0), line=line, w=bw,
                           hl=w in HIGHLIGHT or w.strip(".,!") in ("vitesse", "coureurs", "blesser", "performer")))
        x = placed[-1]["x"] + bw
    # center each line
    for ln in range(line + 1):
        items = [p for p in placed if p["line"] == ln]
        tw = items[-1]["x"] + items[-1]["w"]
        for p in items:
            p["x"] += (W - tw) // 2
    total_h = (line + 1) * lh
    for p in placed:
        p["y"] = 1000 - total_h // 2 + p["line"] * lh + lh // 2
    _card_layout[id(c)] = placed
    return placed


def draw_card(frame, t, c):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tc = TIER_COLORS[c["tier"]]
    k_in = (t - c["a"]) / 0.25
    # tier reminder badge above the text
    bk = ease_out_back(k_in)
    by = int(560 - 80 * (1 - bk))
    d.rounded_rectangle((W // 2 - 70, by - 70, W // 2 + 70, by + 70), 26, fill=tc)
    d.text((W // 2, by + 6), c["tier"], font=font("Black", 112), anchor="mm", fill=(255, 255, 255),
           stroke_width=3, stroke_fill=(60, 30, 0))
    f = font("Black", 104)
    for p in layout_card(c):
        if p["t"] is None:  # context words already spoken: visible from the start
            k = clamp01(k_in)
            al, sc = k, 1.0
            col = (255, 255, 255)
        else:
            k = (t - p["t"] + 0.04) / 0.16
            if k < 0:
                continue
            al = clamp01(k * 1.5)
            sc = 1.5 - 0.5 * ease_out_back(k, 2.0) if k < 1 else 1.0
            col = tc if p["hl"] else (255, 255, 255)
        if p["t"] is not None and p["hl"]:
            col = YELLOW if c["tier"] != "C" else (255, 70, 55)
        fs = int(104 * sc)
        ff = font("Black", fs) if fs != 104 else f
        cx = p["x"] + p["w"] // 2
        d.text((cx + 5, p["y"] + 8), p["txt"], font=ff, anchor="mm", fill=(0, 0, 0, int(150 * al)),
               stroke_width=8, stroke_fill=(0, 0, 0, int(150 * al)))
        d.text((cx, p["y"]), p["txt"], font=ff, anchor="mm", fill=col + (int(255 * al),),
               stroke_width=8, stroke_fill=(0, 0, 0, int(255 * al)))
    frame.alpha_composite(lay)


# ------------------------------------------------------------- frames
def frame_at(n):
    t = n / FPS
    fr = None

    def canvas():
        nonlocal fr
        if fr is None:
            fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        return fr

    board_on = False
    for idx, b in enumerate(boards):
        if b["a"] <= t < b["b"]:
            draw_board(canvas(), t, b, idx)
            board_on = True
    for c in cards:
        if c["a"] <= t < c["b"]:
            draw_card(canvas(), t, c)
    draw_subtitles(canvas(), t, board_on)
    for fa in FLASH_AT:
        if 0 <= t - fa < 0.17:
            al = int(150 * (1 - (t - fa) / 0.17))
            canvas().alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, al)))
    return fr


# ------------------------------------------------------------- sound design
def build_sfx():
    n = int(TOTAL * sfx.SR) + sfx.SR
    bus = np.zeros(n)

    def put(x, t, g=1.0):
        s = int(t * sfx.SR)
        if s < 0:
            x, s = x[-s:], 0
        e = min(n, s + len(x))
        bus[s:e] += g * x[: e - s]

    put(sfx.impact(0.55), 0.0)
    put(sfx.whoosh(0.5, 0.35, rising=False), 0.0)
    for fa in FLASH_AT:
        put(sfx.whoosh(0.4, 0.45), fa - 0.3)
    for idx, b in enumerate(boards):
        put(sfx.whoosh(0.45, 0.5), b["a"] - 0.3)
        for i in range(4):
            put(sfx.pop(700 + 180 * i, 260 + 60 * i, 0.09, 0.32), b["a"] + 0.04 + 0.05 * i)
        put(sfx.whoosh(0.35, 0.25, rising=False), b["b"] - 0.2)
        if b["card"]:
            put(sfx.riser(0.55, 0.18), b["drop"] - 0.55)
            put(sfx.impact(0.75), b["drop"] - 0.01)
            tier = b["card"][0]
            if tier == "S":
                put(sfx.ding(0.42), b["drop"] + 0.02)
                put(sfx.sparkle(0.28), b["drop"] + 0.08)
            elif tier == "B":
                put(sfx.pop(1200, 500, 0.12, 0.4), b["drop"] + 0.03)
            elif tier == "C":
                put(sfx.fail(0.32), b["drop"] + 0.12)
        if "z" in b:
            put(sfx.bonk(0.5), b["z"])
            put(sfx.scratch(0.25), b["z"] + 0.05)
    for c in cards:
        for t, _ in c["words"]:
            if t is not None:
                put(sfx.tick(0.12), t)
    put(sfx.ding(0.4, 1046.5), RECAP_AT + 0.02)
    put(sfx.sparkle(0.25), RECAP_AT + 0.1)
    import wave
    pcm = np.clip(bus, -1, 1)
    st = (np.stack([pcm, pcm], 1) * 32767).astype("<i2")
    with wave.open("build/sfx.wav", "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sfx.SR)
        wf.writeframes(st.tobytes())


def hue_expr():
    terms = [f"clip(min((t-{b['a']:.3f})/0.2\\,({b['b']:.3f}-t)/0.2)\\,0\\,1)" for b in boards]
    # boards in the source recap are already grayscale; nothing to do there
    m = terms[0]
    for x in terms[1:]:
        m = f"max({m}\\,{x})"
    return f"1-0.85*{m}"


def main():
    build_sfx()
    # desaturate the footage under the board only (keep the burned-in title in colour)
    filt = (f"[0:v]split[top][low];[low]crop={W}:{H - 340}:0:340,hue=s='{hue_expr()}'[lowg];"
            f"[top][lowg]overlay=0:340[bv];"
            f"[bv][1:v]overlay=0:0:format=auto,format=yuv420p[v];"
            "[2:a]acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,"
            "apad=whole_dur=%.3f[vo];" % TOTAL +
            "[3:a]volume=0.75[fx];"
            "[vo][fx]amix=inputs=2:normalize=0:duration=first,"
            "loudnorm=I=-14:TP=-1.0:LRA=9,aresample=48000[a]")
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-i", "build/base.mp4",
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", "build/voice.wav", "-i", "build/sfx.wav",
           "-filter_complex", filt, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "9M", "-bufsize", "18M", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{TOTAL:.3f}", OUT]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    empty = bytes(W * H * 4)
    only = [int(x) for x in sys.argv[2:]]  # optional: render a subset (preview)
    for n in range(NFRAMES):
        if only and n not in only:
            proc.stdin.write(empty)
            continue
        fr = frame_at(n)
        proc.stdin.write(empty if fr is None else fr.tobytes())
        if n % 150 == 0:
            print(f"frame {n}/{NFRAMES}", flush=True)
    proc.stdin.close()
    proc.wait()
    if proc.returncode:
        raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
