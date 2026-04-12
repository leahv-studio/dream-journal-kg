# Dream Journal Knowledge Graph — Build Plan

**Project:** SEIS 666 Final Project, University of St. Thomas  
**Track:** A — Knowledge Graph + AI System  
**Due:** Week 14, May 14 2026  
**Check-in #2:** April 16 (Stage 3 minimum complete)

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Frontend | HTML / CSS / JS | Simple, no build step, runs locally or on GitHub Pages |
| Backend | Python + Flask | Lightweight local server, easy to run on Mac |
| Graph | NetworkX | Just `pip install networkx` — no separate database, graph saves to JSON |
| AI | Claude API (claude-sonnet-4-20250514) | Extraction, analysis, conversational entry |
| Version control | GitHub | Required by rubric; data file evolves visibly over time |

---

## Repo Structure

```
dream-journal-kg/
  /frontend
    index.html        ← entry chat UI
    journal.html      ← graph query + pattern views
    style.css
    app.js
  /backend
    app.py            ← Flask server + API routes
    graph.py          ← NetworkX graph operations
    extract.py        ← Claude API extraction logic
    prompts.py        ← all system prompts in one place
    requirements.txt
  /data
    graph.json        ← persistent graph, committed to repo
    seed_data.py      ← script to load existing dream entries
  schema.json
  SCHEMA.md
  README.md
```

---

## Build Sequence

### Stage 1 — Skeleton
*Goal: frontend and backend talking to each other. No Claude, no graph.*

- [ ] Create GitHub repo
- [ ] Set up Python virtual environment (`python -m venv venv`)
- [ ] Install Flask (`pip install flask flask-cors`)
- [ ] Write `app.py` with one route: `POST /chat` returns `{"response": "hello"}`
- [ ] Write `index.html` with a text input that calls `/chat` and displays the response
- [ ] Confirm it works: type anything in browser, get "hello" back from Python
- [ ] Commit

**Done when:** browser talks to backend, backend responds.

---

### Stage 2 — Graph Foundation
*Goal: schema implemented in NetworkX, graph saves and loads correctly.*

- [ ] Install NetworkX (`pip install networkx`)
- [ ] Write `graph.py` — implement all 8 node types and 15 edge types from schema
- [ ] Write `seed_data.py` — manually encode 10–15 existing dream entries as structured data
- [ ] Confirm graph saves to `data/graph.json` and loads back correctly
- [ ] Write one test query: "show me all dreams" returns list of entries
- [ ] Commit

**Done when:** graph loads, a dream entry can be added programmatically, and a basic query returns results.

---

### Stage 3 — Claude API Extraction
*Goal: paste in a dream narrative, get back structured nodes and edges.*  
**This stage must be complete by April 16 (Check-in #2).**

- [ ] Install Anthropic SDK (`pip install anthropic`)
- [ ] Set up API key in environment variable (never committed to repo)
- [ ] Write extraction prompt in `prompts.py` — instructs Claude to return structured JSON matching schema
- [ ] Write `extract.py` — sends dream narrative to Claude, parses response, writes nodes and edges to graph
- [ ] Test with Grand Am dream entry — confirm extraction output looks correct
- [ ] Wire extraction to `/chat` route — conversation ends, extraction runs, graph updates
- [ ] Build before/after comparison: same dream answered with raw chat vs. graph query
- [ ] Commit

**Done when:** a dream narrative goes in, structured graph data comes out, graph updates.

---

### Stage 4 — Frontend Entry Flow
*Goal: working chat UI that logs a dream and updates the graph.*

- [ ] Build chat interface in `index.html` — message input, conversation display, Claude responses
- [ ] Add "Save to journal" button that triggers extraction on conversation close
- [ ] Build review card — shows extracted nodes before writing to graph, user can edit
- [ ] Add Life Context Window display — current active context always visible, update link
- [ ] Wire context divergence detection — Claude flags when dream themes don't match active context
- [ ] Test full entry flow end to end
- [ ] Commit

**Done when:** user can have a dream conversation, review extracted data, and confirm write to graph — all in the browser.

---

### Stage 5 — Query Views + Demo Polish
*Goal: pattern filter views, before/after demo, presentation-ready.*

- [ ] Build `journal.html` — the graph query and pattern view page
- [ ] Symbol frequency view — bar chart or list of most recurring symbols over time
- [ ] Filter by life context window — show all dreams during a given period
- [ ] Filter by theme — show all dreams expressing a given theme
- [ ] Filter by date range — time-based pattern queries
- [ ] Recurring series view — show full history of a named dream series
- [ ] Before/after demo slide or split view — raw chat vs. graph query on same dataset
- [ ] README written and clean
- [ ] Dry run full 10-minute demo
- [ ] Commit final version

**Done when:** 10-minute demo can be delivered live without notes.

---

### Stage 6 — Graph Visualization + Dashboard
*Goal: interactive graph visualization as the centerpiece of the project, with filter-driven exploration.*

- [x] Add GET /api/graph endpoint — returns D3-ready nodes and links with type metadata
- [x] Add "Graph View" tab to journal.html — force-directed D3.js graph, node coloring by type, legend, hover tooltips, click-to-inspect side panel
- [x] Dream nodes visually larger than other node types
- [x] Dream nodes colored by date gradient (oldest dark → newest bright purple)
- [x] Lens toggle: view by Dreams / Themes / Symbols with radius scaling
- [x] Dream title field on review card; AI-suggested title
- [x] Question limit guard (max 7 exchanges before prompting to save)
- [ ] Dashboard redesign — replace tab navigation with a single-screen layout where the graph is central and filters update what's displayed (design TBD — wireframe in progress)
- [ ] README updated to reflect graph visualization feature
- [ ] Dry run updated demo with graph as centerpiece

**Life Context redesign (Stage 6 addition):**
- [x] Removed `life_phase` from LifeContextWindow schema — replaced with `status`
- [x] New status model: `foreground` / `background` / `dormant` / `archived`
- [x] `end_date` demoted to rarely-used; archiving is the preferred way to mark a context as past
- [x] LifeContextWindow description updated to reflect persistent, state-cycling nature
- [x] `graph.py`: updated `add_life_context_window`, added `update_life_context_status` method
- [x] `app.py`: new `POST /api/life-context-windows` and `PUT /api/life-context-windows/<id>/status`; GET /api/context returns foreground contexts
- [x] Life Context tab in journal.html redesigned as a manage view (Foreground / Background / Dormant / Archive drawer)
- [x] Context chips show status badge (click to cycle), expand on click to show stressors + Edit button
- [x] "Add context" form in manage view
- [x] index.html context banner updated: shows foreground contexts as chips; "Update context" link navigates to manage screen

**Done when:** the graph is the first thing you see, and clicking/filtering updates it in place.

---

## Demo Script (10 minutes)

| Time | What |
|---|---|
| 0:00–1:00 | The problem: show the raw dream chat. Brilliant analysis, but locked, unsearchable, non-cumulative. |
| 1:00–2:30 | The solution: show the graph. Explain the two layers — dream entries + life context windows. |
| 2:30–5:00 | Live entry: log a new dream in the chat UI. Show Claude responding. Show extraction review card. Confirm write to graph. |
| 5:00–7:30 | Pattern queries: "show me all navigation failure dreams." "What themes cluster during transition periods?" Show the before/after delta explicitly. |
| 7:30–9:00 | Recurring series: show the duplex dream series timeline. |
| 9:00–10:00 | Wrap: who would pay for this, what the roadmap looks like, what AI made possible that wasn't before. |

---

## Milestones vs. Class Timeline

| Class milestone | Build stage target |
|---|---|
| April 16 — Check-in #2 | Stage 3 complete, before/after demo ready |
| April 30 — Draft presentation | Stage 4 complete, query views started |
| May 14 — Final delivery | Stage 5 complete, full demo rehearsed |

---

## Key Decisions Already Made

- NetworkX over Neo4j — simpler setup, no separate database, graph as JSON file
- Extraction runs once per entry after conversation closes — not mid-conversation
- `is_recurring` and `is_novel` are user-asserted only — never system-inferred
- Local backend during demo — GitHub Pages for frontend only
- Before/after delta uses Grand Am dream as the anchor example

---

*Leah Vogel · SEIS 666, Spring 2026 · University of St. Thomas*
