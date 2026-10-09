#!/usr/bin/env python3
"""Draw the original cartoon dachshund face used for every app icon (Pillow only).

    python3 tools/draw-dachshund.py   ->  app/assets/source/dachshund-icon-source.png (1024x1024)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app/assets/source/dachshund-icon-source.png"
S = 4            # supersampling
N = 1024 * S

COAT = (186, 104, 48)
COAT_DARK = (128, 66, 28)
COAT_LIGHT = (214, 145, 86)
MUZZLE = (226, 168, 112)
INK = (34, 22, 16)
BLUSH = (255, 128, 128, 110)
TONGUE = (240, 110, 120)


def sc(*v):
    return [x * S for x in v]


def radial_bg():
    small = Image.new("RGB", (256, 256))
    px = small.load()
    c1, c2 = (255, 236, 210), (244, 196, 140)
    for y in range(256):
        for x in range(256):
            d = min(1.0, (((x - 128) ** 2 + (y - 110) ** 2) ** 0.5) / 180)
            px[x, y] = tuple(round(a + (b - a) * d) for a, b in zip(c1, c2))
    return small.resize((N, N), Image.BICUBIC)


def ear(cx, cy, angle, color):
    layer = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = 190, 400
    d.ellipse(sc(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), fill=color)
    return layer.rotate(angle, center=(cx * S, (cy - h / 2 + 40) * S), resample=Image.BICUBIC)


def main():
    img = radial_bg().convert("RGBA")
    # soft shadow under the head
    sh = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse(sc(300, 800, 724, 860), fill=(120, 70, 30, 70))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18 * S)))

    # ears (behind head), long and floppy
    img.alpha_composite(ear(318, 520, -14, COAT_DARK))
    img.alpha_composite(ear(706, 520, 14, COAT_DARK))

    d = ImageDraw.Draw(img)
    # head
    d.ellipse(sc(318, 220, 706, 620), fill=COAT)
    # forehead highlight
    m = Image.new("L", (N, N), 0)
    ImageDraw.Draw(m).ellipse(sc(410, 245, 614, 375), fill=90)
    img.paste(Image.new("RGBA", (N, N), (*COAT_LIGHT, 255)), (0, 0), m.filter(ImageFilter.GaussianBlur(24 * S)))
    d = ImageDraw.Draw(img)
    # long muzzle
    d.rounded_rectangle(sc(410, 420, 614, 790), radius=100 * S, fill=COAT)
    # lighter, gently widening snout (stack of circles = smooth taper)
    for i in range(0, 101):
        t = i / 100
        y = 520 + 200 * t
        r = 66 + 24 * t * t
        d.ellipse(sc(512 - r, y - r, 512 + r, y + r), fill=MUZZLE)

    # blush
    bm = Image.new("L", (N, N), 0)
    bd = ImageDraw.Draw(bm)
    bd.ellipse(sc(352, 500, 424, 548), fill=BLUSH[3])
    bd.ellipse(sc(600, 500, 672, 548), fill=BLUSH[3])
    img.paste(Image.new("RGBA", (N, N), (*BLUSH[:3], 255)), (0, 0), bm.filter(ImageFilter.GaussianBlur(6 * S)))
    d = ImageDraw.Draw(img)

    # eyebrows (tan dots, like a black-and-tan doxie's)
    d.ellipse(sc(398, 350, 446, 380), fill=COAT_LIGHT)
    d.ellipse(sc(578, 350, 626, 380), fill=COAT_LIGHT)

    # big shiny eyes
    for ex in (420, 604):
        ey = 445
        d.ellipse(sc(ex - 44, ey - 46, ex + 44, ey + 46), fill=INK)
        d.ellipse(sc(ex - 26, ey - 32, ex + 2, ey - 4), fill=(255, 255, 255))
        d.ellipse(sc(ex + 10, ey + 10, ex + 24, ey + 24), fill=(255, 255, 255))

    # nose
    d.rounded_rectangle(sc(462, 700, 562, 770), radius=34 * S, fill=INK)
    d.ellipse(sc(482, 710, 516, 728), fill=(110, 96, 90))

    # mouth + tongue
    w = 7 * S
    d.line(sc(512, 770, 512, 792), fill=INK, width=w)
    tg = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    td = ImageDraw.Draw(tg)
    td.rounded_rectangle(sc(492, 790, 532, 846), radius=20 * S, fill=TONGUE)
    td.line(sc(512, 798, 512, 828), fill=(205, 80, 92), width=4 * S)
    img.alpha_composite(tg)
    d = ImageDraw.Draw(img)
    d.arc(sc(462, 752, 514, 800), start=20, end=160, fill=INK, width=w)
    d.arc(sc(510, 752, 562, 800), start=20, end=160, fill=INK, width=w)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").resize((1024, 1024), Image.LANCZOS).save(OUT, optimize=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
