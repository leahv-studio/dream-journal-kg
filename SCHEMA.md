# Dream Journal Knowledge Graph — Schema Reference

**Version:** 1.0  
**Project:** SEIS 666 Final Project, University of St. Thomas  
**Track:** A — Knowledge Graph + AI System

---

## Design Principles

1. **Null is valid everywhere** except required fields. Absence of a value is itself information — a dream with no `notable_color` is not incomplete, it's a dream where color wasn't significant.
2. **`is_recurring` and `is_novel` are user-asserted only.** The system surfaces frequency data separately and never infers these flags automatically.
3. **`co_occurs_with` and `activates` edges are auto-calculated.** All other edges are asserted — by the user or by LLM extraction — with source always tracked.
4. **Extraction runs once per entry, after the conversation closes.** Never mid-conversation. The user reviews the extracted data before it writes to the graph.

---

## Node Types

### Dream
The central hub node. All other nodes connect through it.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | |
| `date` | date | yes | Everything else depends on this. |
| `raw_narrative` | text | no | |
| `emotional_valence` | enum | no | `positive` / `negative` / `mixed` |
| `intensity` | integer 1–5 | no | |
| `visual_quality` | enum | no | `dark` / `normal` / `bright` / `washed_out` / `vivid` |
| `notable_color` | string | no | Only populate when a specific color is conspicuous. Null is meaningful. |
| `language` | string | no | Primary language of the dream. Populate when notable. |
| `is_recurring` | boolean | no | User-asserted only. Never system-inferred. |
| `recurring_series_name` | string | no | User-defined. e.g. "My duplex is way bigger and more messed up than I realized" |
| `status` | enum | no | `active` / `dormant` / `resolved` — for recurring dreams |
| `is_novel` | boolean | no | User-asserted. Marks dreams with genuinely new creative or architectural quality. |
| `age_range` | string | no | For pre-journal dreams. e.g. "ages 4–8" |
| `lucid` | boolean | no | |
| `title` | string | no | Short evocative title. LLM-generated at extraction time; user-editable before confirming. |

---

### Character
Any figure appearing in a dream — real people, animals, creatures, or constructed beings. Renamed from "Person" to reflect that dream figures include non-human entities.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | |
| `name` | string | yes | |
| `character_type` | enum | no | `real_current` / `real_historical` / `constructed` |
| `symbolic_role` | string | no | Free text. Holds interpretive complexity that categorical fields cannot. |
| `language_spoken` | string | no | Only populate when the language a character speaks is notable. |

**character_type values:**
- `real_current` — active real-world relationship
- `real_historical` — real person but functionally symbolic in the dream
- `constructed` — no real-world referent (creatures, composite figures, strangers)

---

### Symbol
A recurring object, image, motif, action, sound, or sensory element that carries symbolic weight.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | |
| `name` | string | yes | |
| `category` | enum | no | `object` / `action` / `animal` / `auditory` / `sensory` |
| `symbolic_note` | string | no | |

---

### Setting
Where the dream takes place. Promoted to its own node type because location carries as much interpretive weight as any symbol.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | |
| `name` | string | yes | |
| `familiarity` | enum | no | `known` / `unfamiliar` / `distorted` |
| `real_or_constructed` | enum | no | `real` / `constructed` / `composite` |
| `symbolic_note` | string | no | |

**real_or_constructed values:**
- `composite` — assembled from multiple real sources, e.g. childhood bedroom + grandparents house

---

### Emotion
A felt state within the dream. Confidence field prevents inferred emotions from being presented as fact.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | |
| `name` | string | yes | |
| `valence` | enum | no | `positive` / `negative` / `ambiguous` |
| `confidence` | enum | no | `stated` / `inferred` / `ambiguous` |

**confidence values:**
- `stated` — user explicitly named this emotion
- `inferred` — LLM read it from the narrative
- `ambiguous` — unclear; valid state, not a failure

---

### Theme
A higher-order interpretive pattern. Can originate from the user or be surfaced by the LLM. Source is always tracked.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | |
| `name` | string | yes | |
| `description` | string | no | |
| `source` | enum | no | `user` / `llm` |

---

### Life Context Window
A persistent waking life context that can move between states of prominence over time. Not tied to a fixed date range — a context can return to foreground after being dormant. Updated occasionally, not per dream entry.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | |
| `label` | string | yes | e.g. "Job search", "Duplex" |
| `start_date` | date | no | |
| `end_date` | date | no | Rarely used. Most contexts don't have a clean end date. Archiving the context is the preferred way to mark it as past. |
| `description` | text | no | Free-text journal entry about this context — what it is, why it matters, how it feels |
| `summary` | text | no | Auto-generated 2–3 sentence summary of `description`. Used in dream analysis prompts instead of the full description to keep context concise. |
| `status` | enum | no | `foreground` / `background` / `dormant` / `archived` |

**status values:**
- `foreground` — active and prominent; shown in the dream entry banner
- `background` — present but not central; not shown in banner
- `dormant` — not currently active; has faded but not formally closed
- `archived` — past, closed out; shown in collapsed archive drawer

---

### Body Sensation
A physical sensation experienced in the dream. Separate from Symbol and Emotion because some dreams are primarily somatic — the sensation is the content, not a visual symbol.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | |
| `description` | string | yes | |
| `location` | string | no | Body region. Free text. |
| `quality` | enum | no | `pain` / `pressure` / `temperature` / `movement` / `other` |
| `confidence` | enum | no | `stated` / `inferred` |

---

## Edge Types

| Edge | From | To | Properties | Auto-calculated |
|---|---|---|---|---|
| `occurred_during` | Dream | Life Context Window | — | no |
| `contains` | Dream | Symbol | `prominence`: background / present / central | no |
| `features` | Dream | Character | `role`: active / passive / observer | no |
| `takes_place_in` | Dream | Setting | `distortion_level`: intact / distorted / unrecognizable | no |
| `evoked` | Dream | Emotion | `anchor`: text, `confidence`: stated / inferred / ambiguous | no |
| `expresses` | Dream | Theme | `strength`: weak / moderate / strong | no |
| `includes_sensation` | Dream | Body Sensation | — | no |
| `contributes_to` | Symbol | Theme | — | no |
| `co_occurs_with` | Symbol | Symbol | `frequency`: integer | **yes** |
| `associated_with` | Character | Theme | — | no |
| `represents` | Character | Symbol | — | no |
| `evokes` | Setting | Theme | — | no |
| `related_to` | Theme | Theme | `relationship_type`: reinforces / contrasts / evolves_into | no |
| `activates` | Life Context Window | Theme | `frequency`: integer | **yes** |
| `recurs_as` | Dream | Dream | `source`: user_asserted | no |

### Auto-calculated edges
- **`co_occurs_with`** — any two Symbol nodes sharing a Dream node get this edge; frequency increments each time they co-appear.
- **`activates`** — derived by analyzing which themes cluster within a Life Context Window, via Dream → Theme edges.

### Note on theme provenance
Theme provenance (`user` vs `llm`) is tracked on the **Theme node** itself via `theme.source`, not on the `expresses` edge. An edge-level `source` property was considered but is not implemented: NetworkX's node_link serialization uses `source` as a reserved key for the edge's origin node ID, so any edge attribute with that name is silently overwritten on save.

### Key queries enabled by edge type
- `occurred_during` — "Show me all dreams during my job search period"
- `co_occurs_with` — "Every time navigation failure appears, what else shows up?"
- `activates` — "Which themes spike during major transition periods vs. stable periods?" *(most powerful query in the system)*
- `recurs_as` — "Show me the full history of the duplex-is-bigger dream series"
- `expresses` + `strength` — "All regression anxiety dreams, strongest first"

---

## Node + Edge Count

| | Count |
|---|---|
| Node types | 8 |
| Edge types | 15 |
| Required fields (total across all nodes) | 16 |
| Auto-calculated edges | 2 |

---

*Dream Journal Knowledge Graph — SEIS 666, Spring 2026, University of St. Thomas*
