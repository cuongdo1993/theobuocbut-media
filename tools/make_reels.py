"""Pre-render the Instagram Reels slideshow for each lesson part (CD 10/11: IG mornings = Reels with music).

bai-hoc/<lesson>/p<i>-reels.mp4 = the carousel images p<i>-1..n.jpg on the cream 9:16 background,
picture 3 s, each text card 42 s, flute + đàn tranh at low volume. 720x1280, small file, served by GitHub Pages
so Instagram can fetch it with video_url (the resumable upload from CI failed with ProcessingFailedError).
Run from the theobuocbut-media folder:  py tools/make_reels.py [lesson-filter]
"""
import glob, json, os, subprocess, sys

MUSIC = "D:/Budda/budda-social/.ci/assets/nhac-sao-tranh.mp3"


def render(frames, out):
    durs = [3.0 if k == 0 else 42.0 for k in range(len(frames))]
    args, chains, off = ["ffmpeg", "-v", "error", "-y"], [], 0.0
    for f, d in zip(frames, durs):
        args += ["-loop", "1", "-framerate", "24", "-t", f"{d + 0.6}", "-i", f]
    args += ["-ss", "15", "-i", MUSIC]
    for k in range(len(frames)):
        chains.append(f"[{k}:v]scale=720:900,pad=720:1280:0:190:color=0xf6eee2,fps=24,format=yuv420p[v{k}]")
    last = "v0"
    for k in range(1, len(frames)):
        off += durs[k - 1]
        chains.append(f"[{last}][v{k}]xfade=transition=fade:duration=0.6:offset={off - 0.6 * k:.2f}[x{k}]")
        last = f"x{k}"
    total = sum(durs) - 0.6 * (len(frames) - 1) + 0.6
    chains.append(f"[{len(frames)}:a]volume=0.35,afade=t=in:d=1.5,afade=t=out:st={total - 2.5:.2f}:d=2.5[a]")
    args += ["-filter_complex", ";".join(chains), "-map", f"[{last}]", "-map", "[a]", "-t", f"{total:.2f}",
             "-c:v", "libx264", "-preset", "medium", "-tune", "stillimage", "-crf", "28", "-profile:v", "high",
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-ar", "44100", "-movflags", "+faststart", "-threads", "2", out]
    subprocess.run(args, check=True)


def main(filt=""):
    for man in sorted(glob.glob("bai-hoc/*/manifest.json")):
        d = os.path.dirname(man)
        if filt and filt not in d:
            continue
        m = json.load(open(man, encoding="utf-8"))
        for i, n in enumerate(m["images"], 1):
            out = f"{d}/p{i}-reels.mp4"
            if os.path.exists(out):
                continue
            render([f"{d}/p{i}-{k}.jpg" for k in range(1, n + 1)], out)
            print(out, round(os.path.getsize(out) / 1e6, 1), "MB", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
