"""Commit + push new videos without keeping them on the PC (CD 15/11: GitHub keeps the videos, the PC clone stays slim).

    py scripts/day_video.py "commit message" shorts/49-ten-moi longs/2027-01-02-ten
    (theobuocbut-media: py tools/day_video.py "msg" video/49-ten-moi.mp4)

Copy the new files into this checkout first (shorts/<name>/video.mp4 + video.json, longs/..., video/...),
without committing them here. The script then:
  1. makes a throwaway partial clone (no video blobs) in a temp folder,
  2. copies the given files into it, commits, pushes with a normal push,
  3. deletes the temp clone and the local copies of those files, then pulls here (blob:none: no video is downloaded).
So no video ever ends up inside this checkout's .git (17/11: committing here kept every video in .git, 4.7 GB).
Files already tracked here (e.g. longs/LICH-DANG-DAI.md) may be passed too; their local edit is pushed and then restored by the pull.
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(cwd, *a):
    print("git", " ".join(a))
    subprocess.run(["git", "-C", cwd, *a], check=True)


def files_under(paths):
    for p in paths:
        full = os.path.join(ROOT, p)
        if os.path.isdir(full):
            for d, _, fs in os.walk(full):
                for f in fs:
                    yield os.path.relpath(os.path.join(d, f), ROOT).replace("\\", "/")
        elif os.path.exists(full):
            yield os.path.relpath(full, ROOT).replace("\\", "/")
        else:
            sys.exit(f"not found: {p}")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    msg, paths = sys.argv[1], sys.argv[2:]
    files = sorted(set(files_under(paths)))
    tracked = set(subprocess.run(["git", "-C", ROOT, "ls-files", "--", *files], capture_output=True, text=True, check=True).stdout.split())
    url = subprocess.run(["git", "-C", ROOT, "remote", "get-url", "origin"], capture_output=True, text=True, check=True).stdout.strip()
    tmp = tempfile.mkdtemp(prefix="day_video_")
    try:
        work = os.path.join(tmp, "repo")
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", url, work], check=True)
        git(work, "sparse-checkout", "init", "--no-cone")
        open(os.path.join(work, ".git", "info", "sparse-checkout"), "w").write("/*\n!*.mp4\n")
        git(work, "checkout", "-q", "main")
        for f in files:
            dst = os.path.join(work, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(ROOT, f), dst)
        git(work, "add", "--sparse", "--", *files)
        git(work, "commit", "-q", "-m", msg)
        git(work, "push", "-q", "origin", "HEAD:main")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # the files are on GitHub now: drop the local copies (untracked ones) / local edits (tracked ones), then pull
    for f in files:
        if f in tracked:
            git(ROOT, "checkout", "--", f)
        elif os.path.exists(os.path.join(ROOT, f)):
            os.remove(os.path.join(ROOT, f))
    git(ROOT, "pull", "-q", "--ff-only", "origin", "main")
    print("pushed; no video kept on the PC (GitHub has it)")


if __name__ == "__main__":
    main()
