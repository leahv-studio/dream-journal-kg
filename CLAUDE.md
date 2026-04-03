# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dream Journal Knowledge Graph — SEIS 666 Final Project, University of St. Thomas (Track A: Knowledge Graph + AI System). A personal dream journaling app that uses Claude for conversational entry and structured data extraction, with a NetworkX knowledge graph as the persistence layer.

**Due:** May 14, 2026 | **Check-in #2:** April 16, 2026 (Stage 3 minimum complete)

## Tech Stack

| Layer | Tool |
|---|---|
| Frontend | HTML / CSS / JS (no build step) |
| Backend | Python + Flask |
| Graph | NetworkX, persisted to `data/graph.json` |
| AI | Claude API — `claude-sonnet-4-20250514` |

## Planned Repo Structure

```
dream-journal-kg/
  frontend/         index.html (chat UI), journal.html (query views), style.css, app.js
  backend/          app.py (Flask + routes), graph.py (NetworkX ops), extract.py (Claude extraction), prompts.py (all system prompts)
  data/             graph.json (persistent graph), seed_data.py (load existing entries)
  schema.json       canonical schema definition
  SCHEMA.md         human-readable schema reference
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

8 node types, 15 edge types. See `Schema files/SCHEMA.md` and `Schema files/schema.json` for full definitions.

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

## Build Stages

The project is built in 5 stages. Current target: Stage 3 by April 16.

1. **Skeleton** — Flask + HTML talking to each other, no Claude, no graph
2. **Graph Foundation** — NetworkX schema implemented, graph.json save/load, seed data
3. **Claude API Extraction** — dream narrative in → structured JSON out → graph updates *(Check-in #2 deadline)*
4. **Frontend Entry Flow** — chat UI, review card, Life Context Window display, context divergence detection
5. **Query Views + Demo Polish** — journal.html pattern views, before/after demo, README

## Demo Anchor

The Grand Am dream entry is the canonical before/after example for the demo — use it consistently when testing extraction and building the comparison view.
