# Dream Journal Knowledge Graph

A personal dream journaling system that uses Claude for conversational entry and structured data extraction, backed by a NetworkX knowledge graph.

**SEIS 666 Final Project — University of St. Thomas, Spring 2026 (Track A: Knowledge Graph + AI System)**

---

## What It Is

You describe a dream in a chat interface. Claude asks follow-up questions to draw out detail, then — when you're ready — extracts structured data from the conversation: symbols, themes, emotions, characters, settings, body sensations. You review the extraction before anything is written. Once confirmed, it's stored as a graph of interconnected nodes.

The query view (`journal.html`) lets you explore patterns across dreams: which symbols recur most, which themes dominate a life context window, what recurring series look like over time.

Seed data is placeholder. Real dreams will be added before demo day.

---

## Tech Stack

| Layer     | Tool                                              |
|-----------|---------------------------------------------------|
| Frontend  | HTML / CSS / vanilla JS (no build step)           |
| Backend   | Python + Flask                                    |
| Graph     | NetworkX, persisted to `data/graph.json`          |
| AI        | Claude API (`claude-sonnet-4-20250514`)           |

---

## How to Run Locally

Every session:

```bash
cd backend
source venv/bin/activate
export ANTHROPIC_API_KEY=sk-...
python app.py
```

First time only (setup):

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

App runs on **http://localhost:5001** (port 5000 is taken by macOS AirPlay Receiver).

The API key must be set as an environment variable — never committed to the repo.

---

## Pages

| Page | URL | Purpose |
|------|-----|---------|
| `dashboard.html` | `http://localhost:5001/dashboard.html` | **Primary app** — unified interface with three sections: Add New (dream entry), Knowledge Graph (interactive visualization + NL query), and Waking Life (life context window management) |
| `journal.html` | `http://localhost:5001/journal.html` | Query & pattern view — symbol frequency, theme filter, life context, date range, recurring series, before/after demo |
| `index.html` | `http://localhost:5001/` | Original standalone chat UI — predates the dashboard redesign; kept for reference but not the active entry point |

---

## Schema Overview

**8 node types:** Dream, Character, Symbol, Setting, Emotion, Theme, LifeContextWindow, BodySensation

**15 edge types:** occurred_during, contains, features, takes_place_in, evoked, expresses, includes_sensation, contributes_to, co_occurs_with\*, associated_with, represents, evokes, related_to, activates\*, recurs_as

\* Auto-calculated. `co_occurs_with` increments when two symbols share a dream. `activates` is derived from Dream→Theme edges within a context window.

See [`SCHEMA.md`](SCHEMA.md) for full field definitions and edge properties.

---

## Design Notes

- `is_recurring` and `is_novel` are user-asserted only — never inferred
- Extraction runs once per entry, after the conversation closes — never mid-conversation
- Null is valid everywhere except required fields (`id`, `date`, `name`, `description`, `label`)
- Emotion and BodySensation confidence fields distinguish `stated` from `inferred` — inferred values are never presented as fact
- The Grand Am dream is the canonical before/after demo anchor
