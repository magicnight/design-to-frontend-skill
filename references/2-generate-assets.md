# Phase 2 · Generate missing assets (OpenAI image API)

Generate the image assets a prototype needs — mascots, banners, hero art, icons — with **true
transparent backgrounds**, then drop them in by the project's naming convention so the UI auto-loads
them. Bundled scripts do the heavy lifting; this file explains how to drive and adapt them.

**First ask: does this asset even need image generation?** A simple single-color UI icon (wallet,
gear, arrow at ~16–32px) is almost always better as an **inline SVG / icon-font glyph** — it's crisp
at any size, recolors with the theme token, never 404s, and costs no API call. Reach for generation
for **rich raster art** — illustrated characters/mascots, photographic banners, hero scenes. When you
do skip generation, still add an image `onError` fallback so a missing/broken asset never shows a torn
image box.

## Why gpt-image-1.5 specifically

- The OpenAI image model `gpt-image-1.5` supports `background=transparent` + `output_format=png`,
  producing a **real alpha channel**. `gpt-image-2` **rejects** `background=transparent` — so for
  cut-out characters/props you must use `gpt-image-1.5`. (For opaque full-bleed banners either works.)
- `/v1/images/generations` makes an image from a text prompt. `/v1/images/edits` takes one or more
  **reference images** and `input_fidelity=high` to keep a character's identity consistent across many
  poses — use edits whenever you're generating variations of an existing character.

## Setup (once)

1. **Key in `.env`** at the project root: create a placeholder `OPENAI_API_KEY=` (and optional
   `OPENAI_BASE_URL=` for a proxy) and ask the user to paste their key in. Never use shell env vars or
   commit the key. The scripts read `.env` (utf-8-sig) and fall back to real env vars.
2. **Python via uv:** `uv venv && uv pip install pillow` (Pillow only needed for the WebP conversion
   step; the generator itself is stdlib-only).

## Generate

Use the bundled `scripts/gen_image.py`. It is a small, stdlib-only client (urllib + manual multipart)
modeled on a production generator. Define your jobs as `(name, size, refs, prompt)` and run.

- **size**: `1024x1024`, `1024x1536` (portrait), or `1536x1024` (landscape). Pick to match the slot.
- **refs**: a list of reference image paths for `/edits` (identity-locked), or `[]` for `/generations`.
- **prompt**: subject + pose/scene + a **transparency style block**. The style block is what actually
  gets you clean cut-outs — be explicit and repeat it:

```
High-quality 3D render, soft studio lighting, whole subject fully visible, nothing cropped.
IMPORTANT: fully transparent background with alpha channel — no floor, no ground shadow, no backdrop,
no checkerboard pattern, no glow or light halo around the subject: alpha must be fully transparent
everywhere except the subject (and the props it holds) themselves.
```

Request params the script sends (don't drop these): `quality=high`, `background=transparent`,
`output_format=png`, `input_fidelity=high` (edits only), `n=1`. It retries on `429`/`5xx` and on
`400 moderation_blocked` with backoff, and saves `out/<name>.png`.

**Identity tips for character variations:** describe the character in full once (fur, clothing, colors,
proportions) and reuse that block verbatim across every pose; pass 1–3 clean reference images; keep
poses in the *new pose:* clause. For two characters in one frame ("duel"), state **"exactly one soccer
ball — never two"**-style constraints, because the model otherwise duplicates shared props.

## Verify the alpha

A PNG can come back looking right but with a baked-in background. Check it with
`scripts/check_alpha.py <file.png>` — it decodes the PNG (stdlib zlib, unfilters scanlines) and reports
corner/edge alpha plus overall `fully_transparent / semi / opaque` percentages. Corners should read
alpha `0`. If they don't, strengthen the transparency style block (call out "no glow/halo", "no ground
shadow") and regenerate. The generator also prints `RGBA(alpha)` vs `NO-ALPHA` per file.

## Convert + place by naming convention

Generated PNGs are large. Convert to web-sized WebP with Pillow (resize to the slot's display width,
`quality 80–82`, `method 6`), then place them where the UI expects.

The point of **naming conventions** is that the UI picks assets up automatically — external developers
drop files in by name and never touch code. Typical pools (adapt to the project's actual scheme, which
phase 1 / its `DESIGN.md` documents):

- **Per-item banners**: `assets/<kind>/<key>.webp` where `<key>` encodes the item (e.g. a match
  banner `m-<day>-<index>.webp`). A `placeholder.webp` is the fallback when a slot has no file.
- **Random pools**: `assets/<pool>-<N>.webp` (N = 1..k) that a component random-picks at mount; the
  pool size lives in a JS array (e.g. `HERO_POOL`).
- Write a small **manifest** (a `MANIFEST.md` / `manifest.json` mapping file → meaning) when an
  external API needs to wire items to their assets.

Bundled converters in the source project (`rename_match_banners.py`, `convert_mybets.py`) are good
templates: walk a source folder, resize to WebP, emit the convention-named files plus a manifest.

## Don't fabricate domain data

Generate **assets** (images) and the **naming/manifest** scaffolding. Do **not** invent the domain
data that drives the UI (schedules, prices, real records) unless asked — that usually comes from the
user's own API. Your job is to make the slots and fill them with art, not to author the dataset.
