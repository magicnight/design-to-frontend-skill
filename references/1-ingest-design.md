# Phase 1 · Ingest the design

Turn a Claude Design prototype into a structured understanding and a living spec (`DESIGN.md`) that
the asset and polish phases — and downstream developers — can work from. The deliverable is *the map*,
not a rewrite.

## What to read, in order

1. **The HTML entry** (e.g. `new ui 2.0.html`). Its `<script type="text/babel" src="src/*.jsx">` list
   is the **file map and load order** — it tells you every module that exists and roughly how they
   layer (tokens/data first, then primitives, then feature modules, then the page orchestrator last).
2. **The design-tokens module** (search for `getTokens`, a `TOKENS`/`FONTS` object, or a colors map).
   Capture the palette, the font stacks, spacing, and which **theme variants** exist (e.g. cyber/dark).
   Everything downstream should reference these tokens, so read them first.
3. **The page orchestrator** (the component that switches between pages/tabs — often the last file).
   It reveals the **navigation tree**: bottom-nav tabs, sub-tabs, and full-screen overlays/drawers.
   From here, map **page → component → data source**.
4. **The data modules** (e.g. `*-data.jsx`). Note the shapes that drive each page and whether they're
   real or placeholder. Downstream the user usually swaps these for their own API — flag which is which.

Use Grep/Glob and an Explore-style sweep rather than reading every file end-to-end. You want the
structure and the seams, not every line.

## Build the asset manifest (feeds phase 2)

Find every image the UI references and split into present vs missing:

- Grep the `src/` for `assets/` string literals and CSS `background-image: url(...)`.
- List the `assets/` directory and diff against referenced paths.
- Note any **naming-convention pools** — places where the code builds a path from data (e.g.
  `` `assets/match/m-${day}-${i}.webp` `` or a `HERO_POOL` array). These are the slots phase 2 fills,
  and the slots external developers drop files into. Record the exact convention and the fallback
  (`placeholder.webp`).

The output is a short list: "these slots are wired but have no file yet" → hand to phase 2.

## Write / refresh DESIGN.md

`DESIGN.md` is the handoff artifact. Keep it skimmable and current. A structure that works:

```markdown
# <App> 设计文档

## 1. 技术与运行        # React+babel, no build; how to preview (the no-cache server); theme
## 2. 导航结构          # bottom nav + sub-tabs + overlays, as a small tree
## 3. 资源 / Banner 约定  # the naming pools, fallbacks, conversion scripts, manifest — the centerpiece
## 4. 页面一览          # table: 页面 | 组件 | 要点 | 截图(link into screenshots/)
## 5. 数据与约定        # data shapes, what's API-driven vs placeholder, font/i18n rules
## 6. 目录              # what lives where
```

Emphasize the **asset/naming conventions** — that section is what lets an external team extend the UI
by dropping files in, without reading code. Link each page row to a capture in `screenshots/`.

## Keep it honest

The prototype's data is usually **placeholder for the user's real API**. Don't present mock numbers as
real, and don't generate the domain dataset during ingest. Record what's wired and what's stubbed; the
user fills the data, you map and (in later phases) fill the visuals and polish.
