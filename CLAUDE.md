# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dream Journal Knowledge Graph — SEIS 666 Final Project, University of St. Thomas (Track A: Knowledge Graph + AI System). A personal dream journaling app that uses Claude for conversational entry and structured data extraction, with a NetworkX knowledge graph as the persistence layer.

**Due:** May 14, 2026 | **Check-in #2:** April 16, 2026 ✓ (complete)

## Tech Stack

| Layer | Tool |
|---|---|
| Frontend | HTML / CSS / JS (no build step) |
| Backend | Python + Flask |
| Graph | NetworkX, persisted to `data/graph.json` |
| AI | Claude API — `claude-sonnet-4-20250514` |

## Repo Structure

```
dream-journal-kg/
  frontend/         dashboard.html (primary app — Add New, Knowledge Graph, Waking Life), journal.html (query views), index.html (original standalone chat UI, pre-redesign), style.css, app.js
  backend/          app.py (Flask + routes), graph.py (NetworkX ops), extract.py (Claude extraction), prompts.py (all system prompts)
  data/             graph.json (persistent graph)
  docs/             index.html (GitHub Pages static demo — full in-browser mock, no backend), data/graph.json (seed data copy for demo), entity-resolution.md, nl-query-design.md (design decision docs)
  schema.json       canonical schema definition
  SCHEMA.md         human-readable schema reference
  STYLE.md          design system — fonts, colors, component conventions
  README.md         project overview
```

## Running the App

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```

App runs on **http://localhost:5001** (port 5000 is taken by macOS AirPlay Receiver).

API key must be set as `ANTHROPIC_API_KEY` environment variable — never committed to repo.

## Graph Schema

8 node types, 15 edge types. See `SCHEMA.md` and `schema.json` for full definitions.

**Node types:** Dream, Character, Symbol, Setting, Emotion, Theme, LifeContextWindow, BodySensation

**Two auto-calculated edges (never assert manually):**
- `co_occurs_with` (Symbol → Symbol) — increments when two symbols share a Dream node
- `activates` (LifeContextWindow → Theme) — derived from clustering Dream → Theme edges within a context window

**All other edges are asserted** by the user or LLM extraction; `source` is always tracked.

## Critical Design Rules

- **`is_recurring` and `is_novel` are user-asserted only** — the system never infers these flags
- **`recurs_as` edges are user-asserted only** — never auto-created
- **Extraction runs once per entry, after the conversation closes** — never mid-conversation; user reviews extracted nodes before any write to the graph
- **Null is valid everywhere** (except required fields) — a missing value is meaningful data, not an error
- **Emotion and BodySensation confidence fields** distinguish `stated` (user named it) from `inferred` (LLM read it from narrative) — inferred values must never be presented as fact
- **Theme source** is always tracked: `user` or `llm`
- **LifeContextWindow active limit is 10** — foreground + background + dormant combined may not exceed 10; archived is unlimited. Enforced at creation time in `POST /api/life-context-windows`. This keeps the journal system prompt and query context compact regardless of how long someone uses the app.

## Build Stages

All stages complete as of May 2026.

1. ✓ **Skeleton** — Flask + HTML talking to each other, no Claude, no graph
2. ✓ **Graph Foundation** — NetworkX schema implemented, graph.json save/load, seed data
3. ✓ **Claude API Extraction** — dream narrative in → structured JSON out → graph updates
4. ✓ **Frontend Entry Flow** — chat UI, review card, Life Context Window display, context divergence detection, title generation, entity resolution at extraction time
5. ✓ **Query Views + Demo Polish** — journal.html, dashboard.html, knowledge graph view, symbol frequency, theme patterns, README
6. ✓ **Natural Language Graph Query** — `POST /api/query`; `build_query_context()` serializes pre-aggregated graph analytics (symbol/theme/character frequency tables, per-LCW breakdowns, dream date index); Claude returns `{highlighted_node_ids, answer}`; KG screen left rail shows answer, graph highlights relevant nodes. See `docs/nl-query-design.md`.
7. ✓ **GitHub Pages Static Demo** — `docs/index.html` is a self-contained copy of the dashboard with a full in-browser mock API layer (no backend, no API key). Seed data loads from `docs/data/graph.json`; all mutations (dream confirm, LCW add/edit/status) update in-memory state only. Chat flow uses scripted Grand Am playback. Deployed at https://leahv-studio.github.io/dream-journal-kg/ (source: `/docs` folder on `main`).

## ⚠️ Two Files, No Auto-Sync

`frontend/dashboard.html` and `docs/index.html` are **completely independent files**. Changes to one have zero effect on the other.

| File | Purpose | Backend | Data |
|---|---|---|---|
| `frontend/dashboard.html` | Live app (localhost:5001) | Flask + real Claude API | `data/graph.json` (real graph) |
| `docs/index.html` | GitHub Pages static demo | None — full in-browser mock | `docs/data/graph.json` (seed copy) |

**When making UI, CSS, or JS changes to `frontend/dashboard.html`, note it in the PR** so the relevant changes can be manually ported to `docs/index.html` before they drift too far. The mock API layer and scripted chat flow in `docs/index.html` are the only parts that don't need porting — everything else (layout, styles, interactions) should stay in sync.

## Demo Anchor

The Grand Am dream entry is the canonical before/after example for the demo — use it consistently when testing extraction and building the comparison view.
