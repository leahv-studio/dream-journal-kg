# Design System — dreama

> **Visual concept:** Dreamy but grounded. Literary, not techy. The app has a point of view — it treats dreaming as a meaningful practice worth documenting carefully, and every design decision reinforces that. Warmth over minimalism, depth over simplicity, intention over convention.

---

## Font System

Three fonts, three registers. Each one has a job and a lane. Do not mix them up.

### `--font-display` — Cormorant Garamond, serif
**The dream voice.** Rare, deliberate, high ceremony.

Used for the wordmark ("dreama") and significant transitions only — moments where the app itself is speaking with unusual weight. `font-weight: 300` for display sizes; `400` for body uses within display contexts.

**Current uses:** `.nav-wordmark`, `.add-wordmark` (empty state)
**If you're unsure whether something warrants Cormorant, it probably doesn't.**

---

### `--font-prose` — Lora, serif
**The reflective voice.** Literary, warm, slightly slower to read — intentionally so.

Used where the app is speaking with care: section titles, assistant responses. The slight resistance of a serif at reading size asks the user to slow down. That's the point.

**Current uses:** `"Waking Life"` heading, `"tell me"` prompt, `.add-msg.assistant` chat bubbles

---

### `--font-ui` — Figtree, sans-serif
**The waking voice.** Clean, friendly, functional.

Everything the user needs to act on or scan quickly: nav links, labels, buttons, form inputs, card metadata, body copy, status text. The entire UI chrome. If it isn't a title or an assistant message, it's Figtree.

**Current uses:** Everything not explicitly listed above.

---

### Font decision guide

| What you're adding | Font to use |
|---|---|
| App wordmark or equivalent | `--font-display` |
| A section title (first heading of a major view) | `--font-prose` |
| AI / assistant spoken text | `--font-prose` |
| A form title, card label, group header | `--font-ui` |
| Button, input, select, badge | `--font-ui` |
| Body copy, descriptions, metadata | `--font-ui` |
| A "significant transition" moment you're confident about | `--font-display` |

---

## Color Palette

### Base surfaces

| Token | Hex | Use |
|---|---|---|
| `--color-bg` | `#F2F0ED` | Page background base |
| `--color-surface` | `#ECEAE6` | Cards, panels, containers |
| `--color-surface-deep` | `#E4E1DC` | Hover states, nested surfaces |
| `--color-border` | `#D8D4CE` | Borders, dividers, separators |

### Ink (text)

| Token | Hex | Use |
|---|---|---|
| `--color-ink` | `#2D2A35` | Primary text, headings |
| `--color-ink-soft` | `#6B6778` | Secondary text, labels |
| `--color-ink-faint` | `#A8A4B5` | Placeholder, muted, disabled |

### Brand & accent

| Token | Hex | Use |
|---|---|---|
| `--color-purple` | `#7C6B9E` | Primary brand, buttons, focus rings |
| `--color-purple-light` | `#B09EC9` | Hover tints, subtle accents |
| `--color-purple-deep` | `#4A3870` | Deep brand, user chat bubbles, wordmark |
| `--color-gold` | `#C9973A` | Life Context Windows, highlights |
| `--color-indigo` | `#3D4E8A` | Theme nodes, graph accents |

### Semantic

| Token | Hex | Use |
|---|---|---|
| `--color-positive` | `#5A8A6A` | Positive emotion valence, success states |
| `--color-negative` | `#A05060` | Negative emotion valence |
| `--color-mixed` | `#8A7A3A` | Mixed or ambiguous valence |

---

## Node Color Palette

Eight node types in the knowledge graph, each with a distinct color. Colors lean muted and dusky to stay coherent against the parchment background.

| Node type | Hex | Character |
|---|---|---|
| **Dream** | `#4A3870` → `#B09EC9` (gradient, old → new) | Purple range; older dreams are deep violet, newer are lavender |
| **Symbol** | `#B08090` | Dusty rose |
| **Theme** | `#3D4E8A` | Deep indigo |
| **Character** | `#7B8EC9` | Periwinkle blue |
| **Setting** | `#5C5868` | Warm grey-violet |
| **Emotion** | `#C47A8A` | Muted coral-rose |
| **Life Context Window** | `#C9973A` | Warm gold |
| **Body Sensation** | `#9B97A8` | Cool lavender-grey |

---

## Background Atmosphere

The page background is a layered radial gradient — a synthetic dusk sky built from four overlapping ellipses over the parchment base (`#F2F0ED`). It is not a uniform wash; it has directional light and depth.

```css
background:
  radial-gradient(ellipse 75% 55% at 52%  4%,  rgba(176,158,201,0.22) 0%, transparent 68%),
  radial-gradient(ellipse 50% 42% at  8% 18%,  rgba( 61, 78,138,0.11) 0%, transparent 58%),
  radial-gradient(ellipse 60% 48% at 14% 78%,  rgba( 74, 56,112,0.19) 0%, transparent 62%),
  radial-gradient(ellipse 65% 38% at 88% 85%,  rgba(201,151, 58,0.15) 0%, transparent 64%),
  var(--color-bg);
```

- **Top center** — soft violet bloom (ambient light source)
- **Upper left** — cool indigo shadow
- **Lower left** — deeper purple-violet ground
- **Lower right** — warm gold horizon

This background does not change between sections. It is the constant atmosphere the entire app lives inside.

**Do not add a solid background to any full-bleed container.** Let the atmosphere breathe through. Frosted or semi-transparent surface colors (`var(--color-surface)`, `rgba(...)`) let the dusk gradient remain visible behind panels.

---

## Waking Life Cards — Gold System

Status hierarchy is communicated through card warmth and depth. Deeper amber = more present in the user's waking life right now. The four statuses form a deliberate intensity sequence within a unified gold-amber family.

### Section title

The "Waking Life" heading uses `#5C3A08` (deep amber) — the same tone as a Foreground label. It anchors the page in its own waking-life register rather than borrowing the dream-purple used by "tell me."

### Status palette

| Status | Card background | Label / badge color | Hex |
|---|---|---|---|
| **Foreground** | Warm amber shimmer + `rgba(252,250,248,0.85)` | Deep amber | `#5C3A08` |
| **Background** | `rgba(248,246,241,0.75)` | Dark gold | `#6E4A14` |
| **Dormant** | `rgba(245,242,237,0.45)` | Medium gold | `#7E5C1E` |
| **Archived** | `rgba(242,240,235,0.26)` | Warm gold | `#8A6820` |

Card borders also use `rgba(201,151,58,…)` at decreasing opacity (0.38 → 0.22 → 0.14 → 0.10) to reinforce the depth sequence.

### Status badge

The badge is plain uppercase text (`font-size: 10px`, `letter-spacing: 0.08em`), no pill. It sits in the **top-right corner** of each card header (right sibling of `.wl-chip-left` in the flex row), so label and date occupy the left column cleanly.

Status is changed via a click-triggered dropdown — the badge is the trigger. The dropdown shows a colored dot + label for each option.

### Left-rail legend

The four status rows in the left rail use `<i class="ti ti-sun">` icons from Tabler Icons (webfont) instead of cloud SVGs. Icon colors match the label colors above.

### Gold vs. purple

The gold palette is intentionally distinct from the brand purple. Life context is waking-world information; purple is the dream register. Do not use `--color-purple` or `--color-purple-deep` anywhere on the Waking Life screen.

---

## Component Conventions

- **Cards** — `border-radius: 12px`, no border (color carries the hierarchy), subtle `filter: brightness` on hover
- **Forms** — `border-radius: 8px–10px`, `var(--color-surface)` background. Focus rings are `var(--color-purple)` everywhere except the Waking Life screen, where they use `rgba(201,151,58,0.65)` (gold).
- **Buttons (primary)** — `var(--color-purple)` fill, white text, `border-radius: 8px`. Exception: Waking Life "Add context" / "Save" buttons use `#6B4410` (dark gold) fill.
- **Buttons (ghost/outline)** — transparent or surface background, border `var(--color-border)`, text `var(--color-ink-soft)`
- **Status labels** — plain uppercase text, no pill or badge treatment; `letter-spacing: 0.08em`, `font-size: 10px`
- **Group headers / section labels** — `font-size: 13px`, `font-weight: 600`, uppercase, `var(--color-ink-soft)`
