# Generating a macOS `.icns` Bundle from Your PNG Icons

You can use the built‑in macOS tools `sips` and `iconutil` to transform your existing PNG icons into a proper `.icns` file. Below is a ready‑to‑run Python script (no argparse) that:

1. Creates a `.iconset` directory next to your PNGs
2. Resizes each PNG for both standard and Retina (@2×) slots
3. Packs everything into `icon.icns`

```python
#!/usr/bin/env python3
from pathlib import Path
import subprocess

# ──────────────────────────────────────────────────────────────────────────
# HARD‑CODED PATHS (adjust if needed)
# ──────────────────────────────────────────────────────────────────────────
# Master PNG directory (generated earlier)
ICON_DIR = Path(
    r"C:\Users\Alif\Documents\GitHub\stride-studio\stride-studio\stride_studio\gui\icons"
)
# Name of the .iconset folder to create
ICONSET = ICON_DIR / "StrideStudio.iconset"
ICONSET.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────
# DEFINE SIZES (pts) FOR macOS SLOTS (standard + Retina)
# ──────────────────────────────────────────────────────────────────────────
# These correspond to: 16, 32, 128, 256, 512 points
POINT_SIZES = [16, 32, 128, 256, 512]

# ──────────────────────────────────────────────────────────────────────────
# PROCESS EACH SIZE
# ──────────────────────────────────────────────────────────────────────────
for pt in POINT_SIZES:
    src_png = ICON_DIR / f"icon_{pt}x{pt}.png"
    # Standard slot
    out_std = ICONSET / f"icon_{pt}x{pt}.png"
    subprocess.run([
        "sips", "-z", str(pt), str(pt), str(src_png), "--out", str(out_std)
    ], check=True)

    # Retina (@2×)
    out_ret = ICONSET / f"icon_{pt}x{pt}@2x.png"
    subprocess.run([
        "sips", "-z", str(pt*2), str(pt*2), str(src_png), "--out", str(out_ret)
    ], check=True)

# ──────────────────────────────────────────────────────────────────────────
# PACK INTO AN .icns
# ──────────────────────────────────────────────────────────────────────────
icns_out = ICON_DIR / "icon.icns"
subprocess.run([
    "iconutil", "-c", "icns", str(ICONSET), "-o", str(icns_out)
], check=True)

print(f"✅ Generated macOS icon bundle: {icns_out}")
```

## How to Run

1. **Ensure you're on macOS** and have both `sips` and `iconutil` (shipped by default).
2. **Install** Python environment if you haven't already (Python 3.x).
3. **Save** the above script as `gen_icns.py` (or `.sh` if you convert to pure shell).
4. **Execute** from any location:
   ```bash
   python gen_icns.py
   ```

You'll end up with:

```text
.../gui/icons/
└── StrideStudio.iconset/
    ├ icon_16x16.png
    ├ icon_16x16@2x.png
    ├ icon_32x32.png
    ├ icon_32x32@2x.png
    ├ icon_128x128.png
    ├ icon_128x128@2x.png
    ├ icon_256x256.png
    ├ icon_256x256@2x.png
    ├ icon_512x512.png
    └ icon_512x512@2x.png

.../gui/icons/icon.icns
```

Use `icon.icns` in your macOS bundle. If you need a pure shell version or further integration tips, let me know!

