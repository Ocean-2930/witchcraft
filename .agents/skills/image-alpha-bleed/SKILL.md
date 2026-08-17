---
name: image-alpha-bleed
description: Remove white or dark edge halos from transparent PNG sprites and generated raster assets by propagating nearby opaque colors into low-alpha pixels without changing the alpha channel. Use during asset creation or preprocessing when transparent images show matte fringes after scaling, filtering, mipmapping, atlas packing, FFmpeg processing, or Pygame rendering; do not run it every game frame.
---

# Image Alpha Bleed

Apply alpha bleed as an offline asset-build step. Never add this processing to the application render loop.

## Workflow

1. Confirm the input is a PNG with a real alpha channel. If it is RGB-only or contains a baked checkerboard, regenerate or extract transparency first; alpha bleed cannot discover the silhouette.
2. Run `scripts/alpha_bleed.py` with a new output path. Preserve the source unless the user explicitly requests replacement.
3. Inspect the result over both light and dark solid backgrounds.
4. Run `--check` on the result. Verify that the alpha channel is unchanged and the suspicious low-alpha matte ratio decreased.
5. Replace the production asset only after visual and numeric verification.

## Commands

```powershell
python scripts/alpha_bleed.py sprite.png
python scripts/alpha_bleed.py sprite.png --output sprite-clean.png --radius 8 --edge-alpha 64
python scripts/alpha_bleed.py sprite-clean.png --check
```

The default output is `<stem>-alpha-bleed.png`. `--radius` controls how far colors extend into fully transparent pixels. `--edge-alpha` controls which low-alpha edge pixels receive propagated RGB. Larger values remove stronger matte contamination but can flatten intentionally soft translucent artwork.

## Guardrails

- Preserve every alpha value exactly; change RGB only.
- Use this for hard-edged sprites, icons, texture atlases, and cutouts. Review smoke, glow, glass, and other intentionally translucent art carefully.
- Reject RGB-only inputs with a clear error.
- Do not treat a checkerboard drawn into RGB pixels as transparency.
- Prefer 4–12 pixels of bleed for sprites that will be downscaled. Start with `--edge-alpha 64`.
- Keep output dimensions and PNG metadata-independent pixel layout unchanged.

