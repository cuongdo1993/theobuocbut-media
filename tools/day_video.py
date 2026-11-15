"""Commit + push new videos from this slim checkout (CD 15/11: no mp4 kept on the PC, GitHub keeps them).

    py scripts/day_video.py "commit message" shorts/49-ten-moi longs/2027-01-02-ten   (theobuocbut-media: py tools/day_video.py "msg" video/49-ten-moi.mp4)

The local clone uses sparse-checkout "/*" + "!*.mp4": mp4 files are not in the working tree.
A new video copied into shorts/, longs/ (or video/ in theobuocbut-media) is added with
`git add --sparse`, committed, pushed with a normal push, then `git sparse-checkout reapply`
removes the mp4 from the disk again. GitHub (and the CI) still has every video.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*a):
    print("git", " ".join(a))
    subprocess.run(["git", "-C", ROOT, *a], check=True)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    msg, paths = sys.argv[1], sys.argv[2:]
    git("add", "--sparse", "--", *paths)
    git("commit", "-m", msg)
    git("push", "origin", "HEAD")
    git("sparse-checkout", "reapply")
    print("pushed; local mp4 removed from the working tree (GitHub keeps it)")


if __name__ == "__main__":
    main()
