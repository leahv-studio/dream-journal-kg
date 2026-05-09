# Dream Journal Knowledge Graph

A personal dream journaling system that uses Claude for conversational entry and structured data extraction, backed by a NetworkX knowledge graph.

**SEIS 666 Final Project — University of St. Thomas, Spring 2026 (Track A: Knowledge Graph + AI System)**

---

## What It Is

You describe a dream in a chat interface. Claude asks follow-up questions to draw out detail, then — when you're ready — extracts structured data from the conversation: symbols, themes, emotions, characters, settings, body sensations. You review the extraction before anything is written. Once confirmed, it's stored as a graph of interconnected nodes.

The dashboard's Knowledge Graph section lets you explore patterns across dreams — which symbols recur most, which themes dominate a life context window — and query the graph in natural language.

The dream entries in `data/graph.json` are fictional — created to demonstrate the system's features and are not real personal data.

---

## Tech Stack

| Layer     | Tool                                              |
|-----------|---------------------------------------------------|
| Frontend  | HTML / CSS / vanilla JS (no build step)           |
| Backend   | Python + Flask                                    |
| Graph     | NetworkX, persisted to `data/graph.json`          |
| AI        | Claude API (`claude-sonnet-4-20250514`)           |

---

## Live Demo

A static demo is deployed to GitHub Pages:

**https://leahv-studio.github.io/dream-journal-kg/**

The demo loads the full seed dataset and runs entirely in-browser — no backend, no API key required. You can add a dream, change life context window statuses, and explore the knowledge graph. Changes are session-only and disappear when you close the tab.

The "Add New" chat flow uses a scripted playback (the Grand Am entry) rather than live Claude API calls, since API calls can't be made from a static page.

The demo is served from the [`/docs`](docs/) folder on `main`.

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
| `journal.html` | `http://localhost:5001/journal.html` | Pre-redesign query & pattern view — predates the dashboard; kept for reference |
| `index.html` | `http://localhost:5001/` | Pre-redesign standalone chat UI — predates the dashboard; kept for reference |

---

## Demo Mode

Clicking the **dreama** wordmark in the footer toggles demo mode. In demo mode the app loads `data/graph_empty.json` (a blank graph) instead of the live `data/graph.json`, and writes are suppressed — nothing you do in demo mode touches real data. Click the wordmark again to return to the full graph. There's no visible indicator; it just reloads the graph view.

This is useful for showing the empty-state onboarding flow without clearing real data.

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
