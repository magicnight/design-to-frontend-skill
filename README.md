# design-to-frontend

A Claude Code **skill** that takes an existing *Claude Design prototype* — an in-browser
React + `@babel/standalone` HTML mockup (one HTML entry loading `src/*.jsx` + design tokens, **no
build step**) — toward a polished, dev-ready frontend.

> `SKILL.md` is the agent-facing playbook Claude follows when the skill triggers. This README is for
> **humans** — what the skill is, how to install it, and how to use its bundled scripts directly.

## What it does — four activities

Each is a standalone entry point; a from-scratch run goes left to right.

| Activity | What happens | Guide |
|---|---|---|
| **Ingest** | Map the prototype's pages/components/design tokens, find which referenced image assets are missing, write/refresh a `DESIGN.md` spec | `references/1-ingest-design.md` |
| **Generate** | Create missing image assets (mascots/banners/icons) with **transparent backgrounds** via the OpenAI image API, placed by filename convention | `references/2-generate-assets.md` |
| **Build** | Add new pages/components/features the prototype's way (token reuse, `window` registration, nav wiring) | `references/3-polish-frontend.md` |
| **Polish** | Visual hierarchy, interaction/state completeness, mobile ergonomics, i18n, accessibility — each change verified in a real browser | `references/3-polish-frontend.md` |

**Not for:** generic image generation, building a Next.js/Vite/Vue app from scratch, web perf/SEO,
backend, logo design, file conversion, or Figma.

## Install

The skill is a folder (or a `.skill` zip of that folder). Put it where Claude Code discovers skills:

```
~/.claude/skills/design-to-frontend/      # personal — available in every project
# or  <project>/.claude/skills/design-to-frontend/   # project-scoped
```

From a `.skill` file, just unzip it into `~/.claude/skills/` (it expands to `design-to-frontend/`).
Claude lists it in available skills automatically; no restart needed. It triggers on its own when a
request matches (see `SKILL.md`'s `description`) — you don't call it manually.

## Requirements

- **Python 3** + [`uv`](https://docs.astral.sh/uv/) — `uv venv && uv pip install pillow` (Pillow is
  only needed for the PNG→WebP conversion step; the generator and server are stdlib-only).
- **An OpenAI API key** in the *project's* `.env` (`OPENAI_API_KEY=...`) — only for the Generate
  activity. Never hardcode or export it; the scripts read `.env`.
- **A browser driver** (Playwright or a browser MCP) for the verify loop in Build/Polish.

## Bundled scripts (`scripts/`)

All stdlib-only except where noted; run from your project root.

```bash
# 1) Generate transparent-background assets (edit JOBS inside first, put key in .env)
python scripts/gen_image.py                 # all jobs   ·  python scripts/gen_image.py icon_wallet
python scripts/check_alpha.py out/icon_wallet.png   # verify the alpha is real (corners → 0)

# 2) Preview the prototype with a cache-busting server (use a FRESH port after edits)
python scripts/nocache_server.py 8853       # → http://127.0.0.1:8853/<entry>.html
```

`gen_image.py` uses **`gpt-image-1.5`** (not `gpt-image-2`, which rejects `background=transparent`)
and supports both `/images/generations` (from text) and `/images/edits` (reference-locked, to keep a
character consistent across poses).

## Conventions it relies on / teaches

- **Asset naming pools** — the UI auto-loads images by filename (e.g. `assets/<kind>/m-<day>-<n>.webp`,
  random `pool-<N>.webp`), with a `placeholder.webp` fallback. External devs drop files in by name; no
  code change. (Details in guide 2.)
- **Font architecture for multilingual** — body/title text → Latin font (Inter) → Noto Sans SC/JP/KR/…
  so there's no "tofu"; a decorative/`numeric` font (e.g. Orbitron) is reserved for **ASCII only**
  (numbers, currency codes, brand words). (Guide 3, P4.)
- **No-build, verify-in-browser** — edit `.jsx` and reload; babel caches by URL, so bust it with a
  fresh-port no-cache server; confirm 0 console errors + screenshot every change before claiming done.

## Layout

```
design-to-frontend/
├── SKILL.md                       # agent-facing playbook (triggers + cross-cutting rules)
├── README.md                      # this file
├── references/
│   ├── 1-ingest-design.md
│   ├── 2-generate-assets.md
│   └── 3-polish-frontend.md       # build + polish
└── scripts/
    ├── gen_image.py               # OpenAI gpt-image-1.5, transparent PNGs
    ├── check_alpha.py             # verify a PNG's alpha channel
    └── nocache_server.py          # cache-busting static server
```

## Author & license

Created by **Kefeng Zhou** &lt;magicnight@gmail.com&gt;. Released under the MIT License — see [`LICENSE`](LICENSE).
