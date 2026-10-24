"""Step 1: cut the sources into pieces (zoom pushes, b-roll cutaways, blurred card
backgrounds) and concatenate them into build/base.mp4 (video) + build/voice.wav."""
import subprocess
from timeline import PIECES, SOURCES, GAIN_DB, FPS, W, H


def run(cmd):
    subprocess.run(cmd, check=True)


parts = []
for i, p in enumerate(PIECES):
    dur = p["b"] - p["a"]
    out = f"build/piece_{i:02d}.mp4"
    src, ss = SOURCES[p["src"]], p["a"]
    if p["kind"] == "card":
        ss = p["bg"]
        vf = (f"scale={int(W*1.2)}:-2,crop={W}:{H},gblur=sigma=38,"
              f"eq=brightness=-0.18:saturation=1.25")
    else:
        if p["kind"] == "broll":
            src, ss = SOURCES[p["vsrc"]], p["vt"]
        z0 = p["zoom"]
        k = 0.0 if p.get("static") else 0.03  # slow push-in per second
        if p["kind"] in ("broll", "outro"):
            z0, k = 1.06, 0.025
        if z0 == 1.0 and k == 0.0:
            vf = "null"
        else:
            # zoom anchored on the top so the burned-in title stays in frame
            vf = (f"scale=w='trunc({W}*({z0}+{k}*t)/2)*2':h=-2:eval=frame,"
                  f"crop={W}:{H}:(iw-{W})/2:0")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}", "-i", src, "-frames:v", str(round(dur * FPS)),
         "-an", "-vf", vf + f",fps={FPS},format=yuv420p",
         "-c:v", "libx264", "-preset", "fast", "-crf", "12", out])
    parts.append(out)

with open("build/concat.txt", "w") as f:
    for p in parts:
        f.write(f"file '{p.split('/')[-1]}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "build/concat.txt",
     "-c", "copy", "build/base.mp4"])

# Voice: same source intervals, 12 ms fades to avoid clicks at every cut
keys = list(SOURCES)
filt, labels = [], []
for i, p in enumerate(PIECES):
    d = p["b"] - p["a"]
    n = round(d * 48000)
    gain = GAIN_DB[p["src"]] - (8 if p["kind"] == "outro" else 0)
    filt.append(f"[{keys.index(p['src'])}:a]atrim=start_sample={round(p['a']*48000)}:"
                f"end_sample={round(p['a']*48000) + n},asetpts=PTS-STARTPTS,"
                f"aformat=sample_rates=48000:channel_layouts=stereo,volume={gain}dB,apad=whole_len={n},"
                f"atrim=end_sample={n},afade=t=in:d=0.012,afade=t=out:st={d-0.012:.3f}:d=0.012[a{i}]")
    labels.append(f"[a{i}]")
filt.append("".join(labels) + f"concat=n={len(PIECES)}:v=0:a=1[out]")
cmd = ["ffmpeg", "-v", "error", "-y"]
for k in keys:
    cmd += ["-i", SOURCES[k]]
run(cmd + ["-filter_complex", ";".join(filt), "-map", "[out]", "-ar", "48000", "-ac", "2", "build/voice.wav"])
