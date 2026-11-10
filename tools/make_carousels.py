"""Build the Threads morning carousels for every lesson (CD 10/11).

For each lesson in budda-social/posts/bai-hoc-*/post.json:
  text   = newest approved lesson (budda-app commit LESSON_REF, src/content/lessons/<id>.md), app sentences dropped
  parts  = 2 (short) or 3 (longer), split between ## sections, about equal length
  images = bai-hoc/<folder>/p<i>-1.jpg (still from the lesson's video, else the lesson cover)
           + p<i>-2.. text cards (full text of that part, brand style)
  body   = bai-hoc/<folder>/p<i>.txt  (≤500 chars incl. YouTube/TikTok lines)
  bai-hoc/<folder>/manifest.json = {"parts": n, "images": [count per part]}
Run from the theobuocbut-media folder:  py tools/make_carousels.py [folder-filter]
"""
import glob, json, os, re, subprocess, sys, unicodedata
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cards  # noqa: E402

APP, SOCIAL, VIDEOS = "D:/Budda/budda-app", "D:/Budda/budda-social", "D:/Budda/Video/bai-viet-video"
LESSON_REF = os.environ.get("LESSON_REF", "74292fb")
LINKS = "YouTube: https://www.youtube.com/@theobuocbut/shorts\nTikTok: https://www.tiktok.com/@theobuocbut"
APP_WORDS = re.compile(r"(?i)ứng dụng|\bapp\b")


def git_show(path):
    return subprocess.run(["git", "-C", APP, "show", f"{LESSON_REF}:{path}"], capture_output=True,
                          encoding="utf-8").stdout


def lesson_files():
    names = subprocess.run(["git", "-C", APP, "ls-tree", "--name-only", f"{LESSON_REF}", "src/content/lessons/"],
                           capture_output=True, encoding="utf-8").stdout.split()
    out = {}
    for n in names:
        m = re.search(r"^id:\s*(\S+)", git_show(n), flags=re.M)
        if m:
            out[m.group(1)] = n
    return out


def clean(md):
    md = unicodedata.normalize("NFC", md.replace("\r\n", "\n"))
    m = re.match(r"^---\n(.*?)\n---\n", md, flags=re.S)
    title = re.search(r"^title:\s*(.+)$", m.group(1), flags=re.M).group(1).strip() if m else ""
    md = md[m.end():] if m else md
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    md = re.sub(r"(\*\*|__)(\S.*?)\1", r"\2", md)
    md = re.sub(r"(?<!\w)([*_])(\S.*?)\1(?!\w)", r"\2", md)
    paras = []
    for p in md.split("\n\n"):
        p = p.strip()
        if not p or p == "---" or re.search(r"https?://", p):
            continue
        if APP_WORDS.search(p):
            sents = [s for s in re.split(r"(?<=[.!?…])\s+", p) if not APP_WORDS.search(s)]
            p = " ".join(sents).strip()
            if not p or p.startswith("##") and len(p) < 4:
                continue
        paras.append(p)
    return title.strip('"'), "\n\n".join(paras)


def split_parts(body):
    secs = [s.strip() for s in re.split(r"(?m)^(?=## )", body) if s.strip()]
    n = 2 if len(body) <= 3500 else 3
    n = min(n, len(secs))
    total = sum(len(s) for s in secs)
    parts, cur, done = [], [], 0
    for i, s in enumerate(secs):
        cur.append(s)
        done += len(s)
        left = len(secs) - i - 1
        if len(parts) < n - 1 and (done >= total * (len(parts) + 1) / n or left == n - 1 - len(parts)):
            parts.append("\n\n".join(cur))
            cur = []
    if cur:
        parts.append("\n\n".join(cur))
    return parts


def video_dir(title):
    for d in sorted(glob.glob(f"{VIDEOS}/*/")):
        k = os.path.join(d, "KICH-BAN.md")
        if os.path.exists(k):
            first = open(k, encoding="utf-8").readline()
            if title.lower().rstrip("?") in unicodedata.normalize("NFC", first).lower():
                return d
    return None


def still(vdir, i, cover):
    """Picture for part i: the video's own scene image for that part (<letter><i>-01.png ...), else any, else cover."""
    if vdir and os.path.isdir(os.path.join(vdir, "anh")):
        imgs = sorted(f for f in glob.glob(os.path.join(vdir, "anh", "*.png")) if not os.path.basename(f).startswith("_"))
        own = [f for f in imgs if re.match(rf"^[a-z]{i}-\d+\.png$", os.path.basename(f))]
        pick = (own or imgs or [None])[0]
        if pick:
            return pick
    return cover


def crop45(src, dst):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if h / w > 1.25:
        ch = int(w * 1.25); top = (h - ch) // 2
        im = im.crop((0, top, w, top + ch))
    elif h / w < 1.25:
        cw = int(h / 1.25); left = (w - cw) // 2
        im = im.crop((left, 0, left + cw, h))
    im.resize((1080, 1350), Image.LANCZOS).save(dst, quality=88)


def body_text(title, part, i, n):
    head = f"{title} (Phần {i}/{n})"
    first = next(p for p in part.split("\n\n") if not p.startswith("## "))
    tail = f"Lướt ảnh để đọc trọn phần {i}." + (f" Mai mình kể tiếp phần {i + 1}." if i < n else "")
    room = 500 - len(head) - len(tail) - 6
    lead = ""
    for s in re.split(r"(?<=[.!?…])\s+", first):
        if len(lead) + len(s) + 1 > room:
            break
        lead = f"{lead} {s}".strip()
    lead = lead or first[:room - 1].rsplit(" ", 1)[0] + "…"
    return unicodedata.normalize("NFC", f"{head}\n\n{lead}\n\n{tail}")  # CD 10/11: no links in posts, only in the bio


def main(filt=""):
    files = lesson_files()
    for pj in sorted(glob.glob(f"{SOCIAL}/posts/bai-hoc-*/post.json")):
        folder = os.path.basename(os.path.dirname(pj))
        if filt and filt not in folder:
            continue
        post = json.load(open(pj, encoding="utf-8"))
        src = files.get(post.get("lesson_id"))
        if not src:
            print("NO SOURCE", folder); continue
        title, body = clean(git_show(src))
        parts = split_parts(body)
        out = f"bai-hoc/{folder}"
        os.makedirs(out, exist_ok=True)
        for f in glob.glob(f"{out}/*"):
            os.remove(f)
        vdir = video_dir(title)
        cover = os.path.join(os.path.dirname(pj), post.get("image", "vuong.jpg"))
        counts = []
        for i, part in enumerate(parts, 1):
            crop45(still(vdir, i, cover), f"{out}/p{i}-1.jpg")
            made = cards.render(f"{title} (Phần {i}/{len(parts)})", part, f"{out}/p{i}", first_page=2)
            counts.append(1 + len(made))
            t = body_text(title, part, i, len(parts))
            assert len(t) <= 500, (folder, i, len(t))
            open(f"{out}/p{i}.txt", "w", encoding="utf-8", newline="\n").write(t + "\n")
        json.dump({"title": title, "parts": len(parts), "images": counts, "source": f"budda-app {LESSON_REF}:{src}",
                   "video": os.path.basename(vdir.rstrip("/\\")) if vdir else None},
                  open(f"{out}/manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(folder, len(parts), counts, "video" if vdir else "cover")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
