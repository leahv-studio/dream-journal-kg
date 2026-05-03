# Entity Resolution at Extraction Time

## The problem

Without entity resolution, semantically equivalent concepts accumulate as separate nodes. "Phone that won't work" and "lost cell phone" are the same dream symbol, but a naive extraction creates two nodes with no connection — fragmenting the graph and undercounting recurrence. Over time this undermines the "what do I dream about most" view.

## The approach: candidate injection

Before the extraction LLM finalizes its node list, it receives a formatted block of existing graph nodes organized by type. If it recognizes an existing entry as a strong match, it uses that entry's name verbatim — which triggers `write_to_graph`'s existing exact-name deduplication (`_find_node_by_name`) and merges the new occurrence with the existing node rather than creating a new one.

The mechanism lives in two places:

| File | What it does |
|---|---|
| `extract.py` → `build_entity_candidates(dg)` | Serializes existing nodes by type into a formatted string, sorted by connection count |
| `prompts.py` → `EXTRACTION_SYSTEM_PROMPT` | Injects the candidate block as an `EXISTING GRAPH NODES` section before the JSON schema |

The candidates block is built fresh from the live graph on every extraction call in `app.py → api_extract()`.

## Merge vs. create bias by node type

The prompt instructs the model to lean differently for each type:

| Node type | Bias | Reason |
|---|---|---|
| **Symbol** | Merge unless territory is clearly different | "lost cell phone" and "phone that won't work" are the same dream symbol; recurrence should accumulate |
| **Theme** | Merge aggressively | Theme fragmentation hurts pattern detection most — `legitimacy_anxiety` vs `imposter_syndrome` vs `professional_legitimacy_anxiety` should collapse |
| **Character** | Create new unless very strong match | Most characters are contextually specific; "Mom" and "a woman who looked like mom" should stay separate |
| **Setting** | Create new unless clearly the same location | Spatial specificity matters; "undergrad campus" and "childhood home" are distinct even if both involve distortion |
| **Emotion** | No merge guidance needed | Already abstract enough (`Anxiety`, `Dread`) that exact matching handles it |

To adjust these biases, edit the type headers in `_ENTITY_RESOLUTION_SECTION` in `prompts.py`.

## Controlling prompt size as the graph grows

`build_entity_candidates(dg, max_per_type=30)` limits candidates per type. Nodes are sorted descending by connection count before trimming, so the most-recurring nodes (most useful to match against) are always included.

To reduce the candidate block size if the graph grows large: lower `max_per_type` at the call site in `app.py`:

```python
candidates_block = build_entity_candidates(dg, max_per_type=15)
```

With the current graph (~25 symbols, ~15 themes, ~10 characters, ~15 settings, ~15 emotions), the full candidate block adds roughly 80 lines to the prompt — well within comfortable bounds.

## What this does NOT handle

- **Retroactive merging**: existing fragmented nodes (e.g. `sym_confiscated_keys` and `sym_keys`) are not automatically merged. They can be merged manually by editing `graph.json` and repointing edges.
- **User-asserted nodes**: `is_recurring`, `is_novel`, and `recurs_as` edges are never touched by this system — they remain user-asserted only per the schema rules.
- **Characters and settings in the same dream as existing ones**: the model may still create a new node if the match isn't obvious from the name alone. The symbolic_note on symbols and description on themes provide the most signal for matching.
