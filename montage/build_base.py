"""Step 1: cut the source into pieces (zoom pushes, blurred card backgrounds) and
concatenate them into build/base.mp4 (video) + build/voice.wav (audio)."""
import subprocess
from timeline import PIECES, SRC, FPS, W, H

def run(cmd):
    subprocess.run(cmd, check=True)

parts = []
for i, p in enumerate(PIECES):
    dur = p["b"] - p["a"]
    out = f"build/piece_{i:02d}.mp4"
    if p["kind"] == "card":
        ss = p["bg"]
        vf = (f"scale={int(W*1.2)}:-2,crop={W}:{H},gblur=sigma=38,"
              f"eq=brightness=-0.18:saturation=1.25")
    else:
        ss = p["a"]
        z0 = p["zoom"]
        k = 0.0 if p.get("static") else 0.03  # slow push-in per second
        if z0 == 1.0 and k == 0.0:
            vf = "null"
        else:
            # zoom anchored on the top so the burned-in title stays in frame
            vf = (f"scale=w='trunc({W}*({z0}+{k}*t)/2)*2':h=-2:eval=frame,"
                  f"crop={W}:{H}:(iw-{W})/2:0")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}", "-i", SRC, "-frames:v", str(round(dur * FPS)),
         "-an", "-vf", vf + f",fps={FPS},format=yuv420p",
         "-c:v", "libx264", "-preset", "fast", "-crf", "12", out])
    parts.append(out)

with open("build/concat.txt", "w") as f:
    for p in parts:
        f.write(f"file '{p.split('/')[-1]}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "build/concat.txt",
     "-c", "copy", "build/base.mp4"])

# Voice: same source intervals, 12 ms fades to avoid clicks at every cut
filt, labels = [], []
for i, p in enumerate(PIECES):
    d = p["b"] - p["a"]
    filt.append(f"[0:a]atrim=start_sample={round(p['a']*48000)}:end_sample={round(p['b']*48000)},asetpts=PTS-STARTPTS,"
                f"afade=t=in:d=0.012,afade=t=out:st={d-0.012:.3f}:d=0.012[a{i}]")
    labels.append(f"[a{i}]")
filt.append("".join(labels) + f"concat=n={len(PIECES)}:v=0:a=1[out]")
run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(filt),
     "-map", "[out]", "-ar", "48000", "-ac", "2", "build/voice.wav"])
