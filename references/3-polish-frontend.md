# Phase 3 · Build & polish the frontend

Extend the prototype with new pages/components/features AND refine existing ones toward dev-ready
quality. For polishing there are two modes: **review** (the user asks "what can be polished?" → produce
a prioritized, grounded list) and **implement** (the user picks items → make the changes and verify
each in the browser). Don't guess at "polish" — ground every finding in what you actually see rendered.

## Building a new page or component

New work must look like it was always there — match the surrounding code's idiom, not generic React.
The mechanics in this substrate:

- **Reuse, don't reinvent.** Pull colors/spacing from the design tokens and compose the existing kit
  (cards, buttons, chips, banners) before writing anything new. Match the font-token discipline —
  body/title text uses the multilingual token, ASCII-only numbers/brand use the decorative/numeric
  token (see P4). A new component that hardcodes a color a token already names is a smell.
- **Register it.** Write the component as a plain function; export it via `Object.assign(window, {
  Foo })` and reference it as `window.Foo`. Add its `<script type="text/babel" src="src/foo.jsx">` to
  the HTML entry in the right load order (tokens/data → primitives → features → the page orchestrator
  last). A component that isn't registered in the HTML simply won't load.
- **Wire it into navigation.** Either add a tab/route in the page orchestrator, or — for a focused flow
  (a detail page, a sheet, a withdraw/swap-style page) — render it as a **state-driven full-screen
  overlay** (`position:absolute; inset:0`, high z-index, its own back button) that covers the bottom
  nav so the user can't half-navigate underneath it. Remember overlays are state-driven and survive a
  tab switch unless you close them.
- **Drive it from data, not hardcoded values.** Put demo numbers in a data constant with a
  "replace with API" note; the user wires their real API later.

Then verify in the browser exactly as below — a new page is "done" only after it renders with 0
console errors and you've eyeballed it.

## Setup the loop first

1. Start the **no-cache server on a fresh port** (`scripts/nocache_server.py 8853`). Use a *new* port
   whenever you suspect stale babel output — it's the reliable cache-bust.
2. Open the page in a browser (Playwright / browser MCP). Resize to the device's aspect (e.g. a phone
   mockup is ~460×940) so screenshots frame the UI, not desktop whitespace.
3. Confirm a **clean baseline**: 0 console errors (favicon 404 is fine).

Then, for each change: edit the `.jsx` → reload → re-check 0 errors → **screenshot + DOM-verify** the
specific thing changed. Never claim a polish item done off the source diff alone.

## The review framework (P1–P4)

Walk these four lenses; they catch most of what "polish" means for an app UI. Report findings grouped
and **prioritized** (P1 = quick high-impact, down to P4 = production-readiness), each tied to a concrete
location, so the user can pick. Scale depth to the ask.

### P1 · Visual hierarchy & consistency
- **Primary vs secondary actions** must look different. Two equally-loud CTAs side by side is the most
  common miss — give the secondary a muted/outline treatment. Check that a shared button component
  actually *renders* a distinct secondary variant (a `tone="muted"` that silently falls back to the
  primary color is a real bug).
- **Brand/numeric display font vs body font.** Decorative display fonts (geometric, all-caps, sci-fi)
  belong on ASCII-only bits — prices, tickers, brand wordmarks — never on body text. (See the i18n
  note in P4: a Latin-only display font on CJK/accented text renders as a mismatched fallback.)
- **Token discipline.** New work should pull colors/spacing from tokens, not hardcode. Watch for two
  components solving the same thing differently (e.g. two stat-bar styles) — unify them.

### P2 · Interaction & state completeness
- **Validation / insufficient states.** Amount inputs (withdraw, swap, bet) need over-balance and
  ≤0 handling: red field + message + a **disabled submit**. A flow that lets you submit an invalid
  amount silently is incomplete.
- **Submit feedback.** A primary action with no `onClick` or no success signal feels broken even in a
  prototype. A lightweight inline success state (`✓ 已提交`, auto-resets) is enough to make the flow
  read as real.
- **Empty / loading / error states.** Every list needs an empty state; data-backed views need a
  loading skeleton (phase setup time is a good moment to add a reusable `Skeleton`). 
- **Focus.** A bottom-sheet / modal flow should cover the bottom nav so the user can't half-navigate
  underneath it.
- **Accessibility (easy to forget, cheap to add).** Inputs need a `<label>` or `aria-label` and the
  right `inputmode` (`decimal` for amounts); meaningful icons need `role="img"` + `aria-label` (not
  `alt=""`); interactive elements need a visible `:focus-visible` ring for keyboard users. These are
  prototype-cheap and what a dev team will otherwise file back as bugs.

### P3 · Mobile ergonomics
- **Tap targets ≥ ~44px.** Tiny filter chips and icon buttons (padding `4px`, 26px squares) are hard
  to hit — grow the hit area even if the visual stays compact.
- **Safe-area insets.** The bottom nav and top bar need `env(safe-area-inset-*)` (e.g.
  `paddingBottom: max(22px, env(safe-area-inset-bottom))`) so they clear the home indicator / notch on
  real devices. A fixed mockup frame hides this — add it anyway for the real export.
- **Overflow.** Big number inputs should shrink font by length so a large value doesn't shove the unit
  chip off-screen. Long names need ellipsis + `min-width: 0`.

### P4 · i18n & production-readiness
- **Multilingual font architecture.** For any app that will show more than one language: body/title
  text → a Latin font that covers extended scripts (Inter) **→ Noto Sans SC / JP / KR / Arabic / Thai
  → system**, so there's no "tofu". Reserve the decorative/Orbitron-style font for a separate
  `numeric` token used **only on ASCII** (numbers, currency codes, brand words). The CJK fallback must
  be a *loaded web font* (Noto), not a platform font like PingFang that's absent on Windows/Android.
  Load JP/KR/Arabic/Thai **per active locale** (insert the `<link>` on demand) — don't ship every CJK
  webfont always-on.
- **RTL.** If Arabic/Hebrew are in scope, the layout needs `dir="rtl"` mirroring (arrows, alignment,
  flex order) — flag it; it's the biggest gap after fonts.
- **String externalization.** Hardcoded zh/en literals in components won't translate; a real
  multilingual build needs a string table (`tw(lang, key)`).
- **Contrast.** The faintest text tokens at 9–10px on glass often fail legibility — nudge the muted/
  faint token luminance up; it fixes everything at once.
- **Pressed/disabled affordances + demo-data flags.** Add global `button:active`/`button:disabled`
  CSS (inline styles can't do pseudo-classes). Centralize obviously-fake stats into a constant with a
  "replace with API" note.

## Reusable patterns (this design system)

- **Secondary button:** a `muted` variant = subtle bg + neutral border + muted text + no glow, clearly
  below the glowing primary.
- **Loading skeleton:** a shimmer block (`background-position` animation) + a card-shaped composite;
  show once per session on first mount to demo without flashing every visit.
- **Stat bar:** one gradient frosted container with `borderLeft` cell dividers reads cleaner than a
  hairline grid — reuse one treatment everywhere.
- **Validation state:** thread an `invalid` prop into the input/card → red border + red value + message
  + `disabled` submit; on success flip the CTA to a green `✓` state for ~2s.

## Gotchas that waste time

- **Overlay persistence:** a full-screen overlay (drawer/detail) is usually state-driven and *survives
  a bottom-nav tab switch*. Close it before navigating, or your screenshot shows the overlay over the
  wrong page. In automated clicks, an overlay's backdrop blocks the nav underneath — but a programmatic
  `.click()` can still hit a button *under* the overlay and open a second layer; close first.
- **DOM text false positives:** babel's compiled `<script>` contains old string literals, so a source
  substring match isn't proof of render. Verify with a screenshot and computed DOM.
- **React re-render timing:** after a programmatic click, read state in a *separate* call (or `await` a
  short delay inside one `browser_evaluate`) — the same synchronous tick won't see the new render.

## Close out

After a polish pass, **refresh `screenshots/`** (recapture each page) and update the relevant
`DESIGN.md` sections so the spec and visual record match the code. These are what the next developer
inherits.
