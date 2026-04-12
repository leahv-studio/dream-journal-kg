import json
import os
import re
from datetime import date as _date

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

import anthropic
from flask import Flask, Response, jsonify, render_template, request, stream_with_context
from flask_cors import CORS

from extract import extract_dream, write_to_graph, _find_active_context_window
from graph import DreamGraph
from prompts import JOURNAL_SYSTEM_PROMPT, TITLE_SYSTEM_PROMPT

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__, template_folder=FRONTEND_DIR)
CORS(app)

dg = DreamGraph()
try:
    dg.load()
except FileNotFoundError:
    pass

ai = anthropic.Anthropic()
conversation_history: list[dict] = []


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/journal.html")
def journal():
    return render_template("journal.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    conversation_history.append({"role": "user", "content": message})

    def generate():
        full_reply = []
        with ai.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=JOURNAL_SYSTEM_PROMPT,
            messages=conversation_history,
        ) as stream:
            for text in stream.text_stream:
                full_reply.append(text)
                yield f"data: {json.dumps({'delta': text})}\n\n"

        conversation_history.append({"role": "assistant", "content": "".join(full_reply)})
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/extract", methods=["POST"])
def api_extract():
    """
    Run Claude extraction on the current conversation.
    Does NOT write to graph — that happens on /api/confirm.
    Returns extracted data + divergence info for the review card.
    """
    if not conversation_history:
        return jsonify({"error": "No conversation in progress"}), 400

    data = request.json or {}
    dream_date = data.get("date") or _date.today().isoformat()

    extracted = extract_dream(conversation_history, dream_date)

    print("\n" + "=" * 60)
    print("EXTRACTION RESULT")
    print("=" * 60)
    print(json.dumps(extracted, indent=2))
    print("=" * 60 + "\n")

    divergence = _detect_divergence(extracted, dg, dream_date)

    raw_narrative = extracted.get("dream", {}).get("raw_narrative", "")
    suggested_title = ""
    try:
        suggested_title = _generate_dream_title(raw_narrative, extracted)
    except Exception as e:
        print(f"Title generation failed (non-fatal): {e}")

    return jsonify({
        "extracted": extracted,
        "date": dream_date,
        "divergence": divergence,
        "suggested_title": suggested_title,
    })


@app.route("/api/confirm", methods=["POST"])
def api_confirm():
    """Write the reviewed (and possibly user-edited) extraction to the graph."""
    data = request.json or {}
    extracted = data.get("extracted")
    dream_date = data.get("date") or _date.today().isoformat()

    if not extracted:
        return jsonify({"error": "extracted data is required"}), 400

    dream_id = write_to_graph(extracted, dg, dream_date)
    dg.save()

    print(f"\nWritten to graph as: {dream_id}")
    print(f"Graph stats: {json.dumps(dg.stats(), indent=2)}\n")

    conversation_history.clear()
    return jsonify({"dream_id": dream_id, "stats": dg.stats()})


@app.route("/api/discard", methods=["POST"])
def api_discard():
    """Discard the current conversation without saving anything."""
    conversation_history.clear()
    return jsonify({"status": "discarded"})


@app.route("/api/context", methods=["GET"])
def get_context():
    """Return all foreground LifeContextWindow nodes."""
    foreground = [
        {"id": node_id, **attrs}
        for node_id, attrs in dg.G.nodes(data=True)
        if attrs.get("node_type") == "LifeContextWindow"
        and attrs.get("status") == "foreground"
    ]
    return jsonify(foreground)


@app.route("/api/life-context-windows", methods=["POST"])
def create_life_context_window():
    """Create a new LifeContextWindow node."""
    data = request.json or {}
    label = (data.get("label") or "").strip()
    if not label:
        return jsonify({"error": "label is required"}), 400

    start_date = data.get("start_date") or None
    stressors_raw = data.get("stressors", "")
    if isinstance(stressors_raw, str):
        stressors = [s.strip() for s in stressors_raw.split(",") if s.strip()]
    else:
        stressors = list(stressors_raw) if stressors_raw else []
    status = data.get("status") or "foreground"
    if status not in {"foreground", "background", "dormant", "archived"}:
        return jsonify({"error": "invalid status"}), 400

    slug_base = _slug(label[:24])
    lcw_id = f"lcw_{slug_base}"
    # If a node with that id already exists, append a counter
    counter = 1
    base_id = lcw_id
    while lcw_id in dg.G:
        lcw_id = f"{base_id}_{counter}"
        counter += 1

    dg.add_life_context_window(
        lcw_id,
        label=label,
        start_date=start_date,
        stressors=stressors or None,
        status=status,
    )
    dg.save()
    return jsonify({"id": lcw_id, "label": label, "start_date": start_date, "status": status}), 201


@app.route("/api/life-context-windows/<lcw_id>/status", methods=["PUT"])
def update_life_context_status(lcw_id):
    """Update the status of a LifeContextWindow node."""
    data = request.json or {}
    status = (data.get("status") or "").strip()
    if status not in {"foreground", "background", "dormant", "archived"}:
        return jsonify({"error": "status must be one of: foreground, background, dormant, archived"}), 400
    try:
        found = dg.update_life_context_status(lcw_id, status)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not found:
        return jsonify({"error": "not found"}), 404
    dg.save()
    return jsonify({"id": lcw_id, "status": status})


@app.route("/api/dreams")
def get_dreams():
    return jsonify(dg.get_all_dreams())


@app.route("/api/symbols/frequency")
def get_symbol_frequency():
    return jsonify(dg.get_symbol_frequency())


@app.route("/api/themes")
def get_themes():
    return jsonify(dg.get_all_themes())


@app.route("/api/life-context-windows")
def get_life_context_windows():
    return jsonify(dg.get_all_life_context_windows())


@app.route("/api/recurring-series")
def get_recurring_series():
    return jsonify(dg.get_recurring_series())


@app.route("/api/dreams/filter")
def filter_dreams():
    return jsonify(dg.filter_dreams(
        theme=request.args.get("theme"),
        context_window=request.args.get("context_window"),
        start_date=request.args.get("start_date"),
        end_date=request.args.get("end_date"),
        series=request.args.get("series"),
    ))


def _generate_dream_title(raw_narrative: str, extracted: dict) -> str:
    """One-shot call to generate a short evocative title for the dream."""
    themes_text = ", ".join(t["name"] for t in extracted.get("themes", []))
    symbols_text = ", ".join(s["name"] for s in extracted.get("symbols", []))
    user_msg = (
        f"Dream narrative:\n{raw_narrative}\n\n"
        f"Themes: {themes_text or 'none'}\n"
        f"Symbols: {symbols_text or 'none'}\n\n"
        "Generate a title for this dream."
    )
    response = ai.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=60,
        system=TITLE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text.strip().strip('"').strip("'")


def _graph_label(node_type: str, attrs: dict) -> str:
    if node_type == "Dream":
        return attrs.get("date", "?")
    if node_type == "LifeContextWindow":
        return attrs.get("label", "?")
    if node_type == "BodySensation":
        desc = attrs.get("description", "")
        return desc[:40] + "…" if len(desc) > 40 else desc
    return attrs.get("name", "?")


@app.route("/api/graph")
def get_graph():
    nodes = []
    for node_id, attrs in dg.G.nodes(data=True):
        ntype = attrs.get("node_type", "Unknown")
        props = {}
        for k, v in attrs.items():
            if k == "node_type":
                continue
            if k == "raw_narrative" and isinstance(v, str) and len(v) > 220:
                props[k] = v[:220] + "…"
            else:
                props[k] = v
        nodes.append({
            "id": node_id,
            "label": _graph_label(ntype, attrs),
            "type": ntype,
            "properties": props,
        })

    links = [
        {"source": u, "target": v, "type": edata.get("edge_type", k)}
        for u, v, k, edata in dg.G.edges(data=True, keys=True)
    ]
    return jsonify({"nodes": nodes, "links": links})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _detect_divergence(extracted: dict, dg: DreamGraph, date: str) -> dict | None:
    """
    Check whether any extracted themes are new to the current LCW.
    Only fires if the LCW already has established patterns (activates edges).
    Returns a dict with new_themes and context_label, or None.
    """
    lcw_id = _find_active_context_window(dg, date)
    if not lcw_id:
        return None

    # Gather theme names already activated in this context
    activated_names: set[str] = set()
    for u, v, k, d in dg.G.edges(data=True, keys=True):
        if u == lcw_id and d.get("edge_type") == "activates":
            name = dg.G.nodes[v].get("name", "").lower()
            activated_names.add(name)

    # Don't flag if context has no established patterns yet
    if not activated_names:
        return None

    new_themes = [
        t["name"]
        for t in extracted.get("themes", [])
        if t["name"].lower() not in activated_names
    ]
    if not new_themes:
        return None

    return {
        "new_themes": new_themes,
        "context_label": dg.G.nodes[lcw_id].get("label", "your current context"),
    }


if __name__ == "__main__":
    app.run(debug=True, port=5001)
