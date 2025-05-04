#!/usr/bin/env python3
from PIL import Image
from pathlib import Path

# ── HARD-CODED PATHS ─────────────────────────────────────────────────────────
SRC = Path(
    r"C:\Users\Alif\Documents\GitHub\stride-studio\stride-studio\stride_studio\gui\Stride_Studio_icon.png"
)
DST = Path(
    r"C:\Users\Alif\Documents\GitHub\stride-studio\stride-studio\stride_studio\gui\icons"
)

# ── MAKE OUTPUT DIR ──────────────────────────────────────────────────────────
DST.mkdir(parents=True, exist_ok=True)

# ── SIZES TO EMIT ────────────────────────────────────────────────────────────
SIZES = [16, 32, 48, 256]

# ── LOAD MASTER ICON ─────────────────────────────────────────────────────────
img = Image.open(SRC)

# ── GENERATE PNGs ────────────────────────────────────────────────────────────
for s in SIZES:
    out_png = DST / f"icon_{s}x{s}.png"
    img.resize((s, s), Image.LANCZOS).save(out_png)
    print(f"Saved {out_png}")

# ── PACK WINDOWS .ICO ─────────────────────────────────────────────────────────
ico_out = DST / "icon.ico"
img.save(ico_out, format="ICO", sizes=[(s, s) for s in SIZES])
print(f"Saved {ico_out}")
