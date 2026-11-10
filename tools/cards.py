"""Render a lesson part as Threads carousel text cards (1080x1350, brand style)."""
import re, sys, unicodedata
from PIL import Image, ImageDraw, ImageFont

F = "D:/Budda/video-pipeline/fonts/"
BG, INK, ACC, MUTE = "#f6eee2", "#2b2a27", "#2F6B55", "#8a7f70"
W, H, M = 1080, 1350, 92
body_f = ImageFont.truetype(F + "BeVietnamPro-Light.ttf", 42)
bold_f = ImageFont.truetype(F + "BeVietnamPro-SemiBold.ttf", 46)
head_f = ImageFont.truetype(F + "BeVietnamPro-Medium.ttf", 32)
foot_f = ImageFont.truetype(F + "BeVietnamPro-Medium.ttf", 28)
LH, PARA = 64, 34
logo = Image.open("D:/Budda/Social/avatar-threads.png").convert("RGB").resize((56, 56), Image.LANCZOS)
mask = Image.new("L", (56, 56), 0); ImageDraw.Draw(mask).ellipse((0, 0, 55, 55), fill=255)


def wrap(d, text, font, width):
    lines, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def blocks(md):
    """[(kind, lines)] kind = 'h' heading / 'p' paragraph."""
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    out = []
    for para in [p.strip() for p in md.split("\n\n") if p.strip()]:
        if para.startswith("## "):
            out.append(("h", wrap(d, para[3:], bold_f, W - 2 * M)))
        else:
            out.append(("p", wrap(d, para, body_f, W - 2 * M)))
    return out


def render(title, md, prefix, first_page=2):
    """Pick the biggest body size whose last page is not a near-empty orphan."""
    global body_f, bold_f, LH
    for size in (42, 40, 38, 36):
        body_f = ImageFont.truetype(F + "BeVietnamPro-Light.ttf", size)
        bold_f = ImageFont.truetype(F + "BeVietnamPro-SemiBold.ttf", size + 4)
        LH = int(size * 1.52)
        pages = paginate(md)
        if len(pages[-1]) >= 6 or size == 36:
            break
    return draw(title, pages, prefix, first_page)


def paginate(md):
    top, bottom = 190, H - 150
    pages, cur, y = [], [], top
    for kind, lines in blocks(md):
        for k, ln in enumerate(lines):
            need = LH + (14 if kind == "h" and k == 0 and cur else 0)
            if y + need > bottom:
                pages.append(cur); cur, y = [], top
            if kind == "h" and k == 0 and cur:
                y += 14
            cur.append((kind, ln, y)); y += LH
        y += PARA
    if cur:
        pages.append(cur)
    return pages


def draw(title, pages, prefix, first_page):
    total = len(pages) + first_page - 1
    files = []
    for i, page in enumerate(pages, first_page):
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
        d.text((M, 92), title, font=head_f, fill=ACC)
        d.line((M, 150, W - M, 150), fill="#e2d6c3", width=2)
        for kind, ln, y in page:
            d.text((M, y), ln, font=bold_f if kind == "h" else body_f, fill=ACC if kind == "h" else INK)
        im.paste(logo, (M, H - 104), mask)
        d.text((M + 72, H - 92), "Theo Bước Bụt", font=foot_f, fill=MUTE)
        d.text((W - M, H - 92), f"{i}/{total}", font=foot_f, fill=MUTE, anchor="ra")
        f = f"{prefix}-{i}.jpg"; im.save(f, quality=92); files.append(f)
    return files


if __name__ == "__main__":
    src, title, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
    md = unicodedata.normalize("NFC", open(src, encoding="utf-8").read())
    print(render(title, md, prefix))
