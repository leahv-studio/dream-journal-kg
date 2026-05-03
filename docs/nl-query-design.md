# Natural Language Graph Query — Design Document

**Status:** Implemented.  
**Branch:** dashboard-redesign  
**Last updated:** 2026-05-03

---

## Feature Goal

A user types a natural language question ("What did I dream about most in the last 90 days?") into the knowledge graph screen. The app responds with:
- A **text answer** rendered in the left rail — an interpretive, prose response grounded in the graph data
- A **visual highlight** in the force graph — relevant nodes illuminate, everything else dims

This is the primary "before/after delta" demo moment: it demonstrates what the knowledge graph architecture buys you over a flat chat log. A flat log can't answer "which symbols recur most during periods of anxiety" — the KG can, because patterns are encoded as structure rather than buried in prose.

---

## Where the Placeholder Lives

The existing UI has a static `.rail-search` div at the top of the KG screen's left rail (`dashboard.html` around line 1726):

```html
<div class="rail-search">
  <span class="rail-search-icon">⌕</span>
  <span class="rail-search-text">Search the graph</span>
  <span class="rail-search-soon">soon</span>
</div>
```

This div needs to become a real `<input>` + submit flow. The left rail already manages two JS states (`rail-ambient`, `rail-selected`); a third state (`rail-query`) will hold the query answer.

---

## Existing Capabilities We Build On

### Graph query methods (graph.py)

All of these exist today and are already correct:

| Method | What it returns |
|---|---|
| `get_all_dreams()` | All Dream nodes with connected nodes hydrated, sorted by date |
| `get_symbol_frequency()` | Symbols ranked by dream appearance count |
| `get_all_themes()` | Themes with dream counts |
| `get_all_life_context_windows()` | LCW nodes sorted by status then start_date |
| `get_recurring_series()` | Recurring dreams grouped by series name |
| `filter_dreams(theme, context_window, start_date, end_date, series)` | Multi-param filter, any subset |
| `stats()` | Node and edge counts by type |

The `/api/stats` endpoint in `app.py` already does date-windowed aggregation (top theme last 90 days, top symbol all time) inline — the pattern is established.

### Claude API call patterns (app.py, extract.py)

Four call patterns exist. The new query feature fits the **one-shot JSON** pattern:

| Pattern | Location | Style | Purpose |
|---|---|---|---|
| Streaming conversation | `app.py /chat` | `ai.messages.stream()` | Multi-turn journaling |
| One-shot extraction | `extract.py extract_dream()` | `client.messages.create()` | Conversation → structured JSON |
| One-shot title | `app.py _generate_dream_title()` | `ai.messages.create()` | Short title |
| One-shot LCW summary | `app.py _generate_lcw_summary()` | `ai.messages.create()` | 2-3 sentence summary |

The query call follows the same pattern as extraction: build a context block, call Claude, parse the JSON response. The markdown-fence-stripping logic in `extract_dream()` can be reused verbatim.

### Graph highlight (dashboard.html)

`applyEgoHighlight(nodeId)` already exists (~line 2393). It dims everything except a single node and its direct neighbors. The query feature needs a parallel `applySetHighlight(nodeIds)` that accepts an arbitrary set of node IDs and dims everything not in the set.

---

## Architecture Decision: One-Call with Pre-Aggregated Context

### What was considered

**Option A — Two-call (parse intent → run query → interpret results):** Claude first returns structured query parameters, Python executes the matching graph methods, Claude interprets the results. Perfectly scalable, but adds latency and requires enumerating a "query vocabulary" Claude must select from.

**Option B — One-call with raw graph dump:** Serialize every dream with all its connections, send to Claude, let Claude do its own traversal. Simple but doesn't scale (see Scaling section below).

**Option C — One-call with pre-aggregated context (chosen):** Python pre-computes analytical summaries (frequency tables, per-LCW breakdowns) and passes those to Claude. Claude interprets and responds in JSON. No raw dream enumeration.

### Why Option C

The whole point of the knowledge graph is that Python already did the counting. Claude's role in the query is to *interpret pre-computed results*, not to re-derive them from raw entries. This maps naturally to what each system is good at: Python for exact graph traversal, Claude for natural language interpretation.

It also means the token budget is bounded by the number of distinct concepts (Symbols, Themes, Characters, LCWs), not the number of dreams — and distinct concepts grow slowly due to entity resolution and merging.

---

## Scalability Analysis

### The core concern

Serializing per-dream entries scales linearly with usage. Even a compact entry:

```
[dream_2026_04_01] 2026-04-01 — symbols: car, keys; themes: loss of control, nostalgia
```

is ~25 tokens. At 365 dreams that's ~9,000 tokens of dream list alone. At 730 dreams, ~18,000. Still within Claude Sonnet's 200K context, but:
- Claude's reasoning quality degrades over large undifferentiated lists ("lost in the middle")
- Every query pays the full token cost whether or not the question needs it
- Cost per query climbs with usage

### Why distinct-concept nodes don't have this problem

| Node type | Scales with | Growth rate |
|---|---|---|
| Dream | Every entry | Linear — ~365/year |
| Symbol | Distinct concepts | Slow — entity resolution merges aggressively |
| Theme | Distinct patterns | Very slow — maybe 60–80 even at year 2 |
| Character | People who appear | Slow — real people recur |
| LifeContextWindow | Life chapters | Very slow — maybe 10–20 lifetime |

A two-year, 730-dream graph might have 200 symbols, 80 themes, 150 characters. A frequency table for those fits in ~3,000 tokens and doesn't grow meaningfully after concepts plateau.

### The dream index

Some questions need to name specific dreams: "Which dreams involved my sister?" The answer should say something like "dreams from March 4th, April 12th, and May 1st." That requires a compact index of dream node IDs to dates.

**Date is the correct identifier — not title.** Date is the semantic identity for a Dream node in this schema: the node ID encodes it (`dream_2026_04_01`), `get_all_dreams()` sorts by it, and all date-windowed queries key off it. Title was added later as a UX nicety and is nullable. Using dates in the index is correct and more useful for temporal reasoning.

Index entry format: `[dream_2026_04_01] 2026-04-01`

Edge case: same-day dreams get `dream_2026_04_01_2` (from `_unique_id()` in `extract.py`). Two index entries, same display date, different IDs. Harmless — Claude includes both in any date-range result.

**Cap the dream index at 180 days.** This covers roughly 6 months of daily logging (~180 entries × ~15 tokens = ~2,700 tokens). Questions about older entries fall back to the text answer without graph highlighting. Note the limitation in the UI ("query looks back up to 6 months"). This is the safety valve that keeps token cost stable regardless of how long someone has used the app.

---

## What `build_query_context()` Should Produce

A new Python function (in `app.py` or a new `query.py`) that returns a compact string in this shape:

```
GRAPH OVERVIEW
  Total: 47 dreams, 62 symbols, 28 themes, 34 characters, 4 life context windows

SYMBOLS — all time (by dream frequency):
  [sym_car] "car" — 12 dreams
  [sym_water] "water" — 9 dreams
  ...

SYMBOLS — last 90 days:
  [sym_car] "car" — 5 dreams
  ...

THEMES — all time:
  [thm_loss_of_control] "loss of control" — 8 dreams
  ...

THEMES — last 90 days:
  [thm_loss_of_control] "loss of control" — 3 dreams
  ...

CHARACTERS — all time:
  [char_mom] "Mom" — 7 dreams
  ...

LIFE CONTEXT WINDOWS:
  [lcw_grad_school] "Grad school application season" (foreground, started 2025-09-01)
    Dreams in this window: 23
    Top themes: academic anxiety ×9, imposter syndrome ×6, transition ×4
    Top symbols: building ×7, car ×5, keys ×3

DREAM INDEX — last 180 days (date → node ID):
  [dream_2026_04_01] 2026-04-01
  [dream_2026_03_28] 2026-03-28
  ...
```

**What is explicitly excluded:**
- `raw_narrative` — never included, ever. This is the whole point.
- Full emotion lists per dream
- BodySensation nodes (too granular for pattern queries; not frequency-trackable)
- Individual dream-level symbol/theme/character lists beyond what's reflected in frequency tables

**Estimated token budget:** ~3,000–4,500 tokens for a mature graph (year 2+). Flat and predictable.

---

## The `/api/query` Endpoint

New route in `app.py`, ~50 lines following the extraction pattern:

**Request:** `POST /api/query` with `{"question": "What did I dream about most in the last 90 days?"}`

**Claude prompt structure:**
- System: "You are a dream journal analyst. You have access to structured data from the user's knowledge graph. Answer the user's question using only the data provided. Return JSON only."
- Context block: output of `build_query_context()`
- User message: the question

**Claude response format:**
```json
{
  "highlighted_node_ids": ["sym_car", "sym_water", "thm_loss_of_control"],
  "answer": "In the last 90 days, the car symbol has appeared most frequently..."
}
```

`highlighted_node_ids` must contain node IDs as they appear in the context block (bracketed). Including IDs in the context block directly avoids any name-to-ID lookup step server-side.

**Flask response:** pass `highlighted_node_ids` and `answer` straight to the frontend.

---

## Frontend Changes

### 1. Convert the placeholder to a real input

Replace the static `.rail-search` div with an `<input type="text">` + submit (Enter key or button). The "soon" badge is removed.

### 2. Add a third rail state: `rail-query`

The left rail currently manages two states:
- `rail-ambient` — default graph-at-a-glance view
- `rail-selected` — shown when a node is clicked

Add `rail-query` — shown after a query returns. Displays the prose answer. Include a close/clear button that returns to `rail-ambient` and clears the graph highlight.

### 3. Write `applySetHighlight(nodeIds)`

Parallel to `applyEgoHighlight(nodeId)` (~line 2393 of `dashboard.html`). Instead of ego-network expansion, it takes an arbitrary set of node IDs and applies the same dim/highlight treatment to exactly those nodes. Nodes not in the set get `opacity: 0.07`. Edges connecting any two highlighted nodes stay visible; all others dim.

---

## Demo Script Notes

- The Grand Am dream is the canonical demo entry per CLAUDE.md — verify it produces useful query responses before the presentation
- Start the demo in the populated graph, not demo mode (empty graph produces nothing to query)
- Good demo questions to test against the actual seed data:
  - "What did I dream about most?" — should surface top symbols and themes
  - "What themes came up during [LCW name]?" — exercises LCW → theme traversal
  - "Which symbols appear most often?" — cleanest, most visual graph highlight
  - "What's been recurring lately?" — exercises date-windowed symbol/theme frequency

---

## Limitations (by design)

**Not answerable by this feature:**
- "What did I dream about after my breakup?" — semantic similarity over raw narratives; this is a vector search problem, not a KG query problem. The system should respond gracefully: "I can surface patterns in your graph, but I can't search the content of individual dreams."
- Dream-level detail older than 180 days — beyond the dream index cap
- Questions about BodySensation patterns — not included in query context (too granular)

**These limitations are intentional.** The scope boundary between "what the KG knows" and "what only the raw text knows" is itself a demo moment. It makes the architecture choice concrete.

**`is_recurring`, `is_novel`, `recurs_as`** — user-asserted only per the critical design rules. The query feature does not infer or surface these unless the user has explicitly set them.

---

## Files to Create/Modify

| File | Change |
|---|---|
| `backend/app.py` | Add `POST /api/query` route; add `build_query_context()` function |
| `backend/prompts.py` | Add `QUERY_SYSTEM_PROMPT` |
| `frontend/dashboard.html` | Convert placeholder to input; add `rail-query` state; add `applySetHighlight()` |

No new files strictly required. If `build_query_context()` grows complex, extracting it to `backend/query.py` is reasonable but not necessary for the demo.
