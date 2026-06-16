---
name: design-to-frontend
description: >-
  Pipeline for taking an existing Claude Design prototype — an in-browser React + babel-standalone
  HTML mockup (one HTML entry loads src/*.jsx + design tokens, no build step) — toward a polished,
  dev-ready frontend, in four activities: INGEST it (map pages/components/tokens, find missing assets,
  write a DESIGN.md); GENERATE its missing image assets (mascots/banners/icons via the OpenAI image
  API — gpt-image-1.5, transparent backgrounds — placed by filename convention); BUILD new
  pages/components/features; POLISH it (visual hierarchy, states, mobile, i18n, a11y) — each verified
  in a real browser. Trigger when the user works on such a prototype (or names one like
  "new ui 2.0.html") and asks to ingest it, find/fill its missing image assets, preview it locally,
  build a page or feature in it, or polish/打磨 it — even if just one. NOT for: generic image
  generation, building a Next.js/Vite/Vue app from scratch, web perf/SEO, backend, logo design, file
  conversion, or design tools like Figma.
---

# Design → Frontend pipeline

Turn a Claude-generated design prototype into a polished, dev-ready frontend across four activities —
**ingest, generate, build, polish** — each a standalone entry point. They map to three reference
guides (build & polish share one). Figure out which the request needs, then read the matching guide.

| Guide | When the request is about… | Read |
|---|---|---|
| **1 · Ingest design** | "parse this design", "what's in the prototype", building a spec/DESIGN.md, mapping pages/components/tokens, finding what assets are missing | [references/1-ingest-design.md](references/1-ingest-design.md) |
| **2 · Generate assets** | "generate/make the missing mascots/banners/icons", transparent-background images, filling an asset pool, gpt-image-1.5, converting to WebP | [references/2-generate-assets.md](references/2-generate-assets.md) |
| **3 · Build & polish** | building a new page/component/feature on the prototype, OR "polish/refine/打磨 this page" — visual hierarchy, states/validation, mobile/i18n/a11y, "make a preview and check it" | [references/3-polish-frontend.md](references/3-polish-frontend.md) |

Most real requests touch one activity. A from-scratch run goes ingest → generate → build → polish.
Don't read a guide you don't need.

## The substrate you're working in

Claude Design prototypes are **single-file-ish in-browser React apps**, not a build pipeline. Knowing
this shape prevents most mistakes:

- **React 18 + `@babel/standalone`** loaded from CDN. One HTML entry (e.g. `new ui 2.0.html`) lists
  every `<script type="text/babel" src="src/*.jsx">` in load order. There is **no bundler, no `npm run
  build`** — you edit `.jsx` and reload.
- Components are plain function declarations exported with `Object.assign(window, { Foo, Bar })` and
  referenced as `window.Foo` or bare globals across files (classic-script global scope). Adding a new
  component = write the function, add it to a `window` assign, and register its file in the HTML.
- **Design tokens** (colors, fonts, spacing) live in a tokens module (e.g. `getTokens('cyber','dark')`).
  Read tokens before styling so new work matches; never hardcode a color that a token already names.
- **Assets** are referenced by path and often by **naming convention** (filename pools) so the UI
  auto-picks them — see phase 2. External devs are expected to drop files in by name, not edit code.

## Cross-cutting rules (apply in every phase)

These are the lessons that, skipped, cost the most rework:

1. **Babel caches transpiled JSX by URL.** After editing a `.jsx`, a normal reload often serves the
   *old* compiled code. Bust it by serving over a **no-cache server on a fresh port** (bundled
   `scripts/nocache_server.py`, e.g. `python nocache_server.py 8853`) — a new port guarantees a clean
   compile. This single habit avoids hours of "my change isn't showing up".
2. **Verify every change in a real browser before claiming it works.** Use Playwright (or the
   available browser MCP): navigate, confirm **0 console errors** (a favicon 404 is harmless), then
   check the change **visually with a screenshot** and the DOM with `browser_evaluate`. Searching the
   raw page source for text gives **false positives** — babel's compiled `<script>` still contains the
   old string literals, so a substring match is not proof the UI rendered. Trust the screenshot and
   computed DOM, not source text.
3. **API keys go in the project `.env`.** Create a placeholder `.env` (e.g. `OPENAI_API_KEY=`) for the
   user to fill; read it at runtime. Never ask the user to export env vars, never hardcode or commit a
   key. The bundled `gen_image.py` already reads `.env` this way.
4. **Python deps via `uv`** (`uv venv` + `uv pip install pillow`), not `python -m venv`/`pip`. Image
   conversion (PNG → web-sized WebP) via Pillow.
5. **Keep a living spec + visual record.** Maintain a `DESIGN.md` (pages, components, tokens, asset
   conventions) and a `screenshots/` folder of current page captures. Refresh them when the design
   changes — they are the handoff artifact for downstream developers.

## Working rhythm

Explore before acting (read the tokens, the target component, the data shape), make the change, then
**verify in the browser**. For multi-item work, do a quick pass to discover the work-list (which files,
which asset slots, which pages) before fanning out. State findings plainly; if a check fails, say so
with the evidence rather than asserting success.

When a request is a broad "polish this", don't guess — run the review framework in
[references/3-polish-frontend.md](references/3-polish-frontend.md) to produce a prioritized,
grounded list first, then implement what the user picks.
