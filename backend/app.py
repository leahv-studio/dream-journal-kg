import json
import os
from datetime import date as _date

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

import anthropic
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from extract import extract_dream, write_to_graph
from graph import DreamGraph
from prompts import JOURNAL_SYSTEM_PROMPT

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__, template_folder=FRONTEND_DIR)
CORS(app)

# Graph — loaded once at startup; reloaded on each extraction write
dg = DreamGraph()
try:
    dg.load()
except FileNotFoundError:
    pass  # empty graph until seed_data.py is run

# Anthropic client
ai = anthropic.Anthropic()

# In-memory conversation history (single session; clears after each extraction)
conversation_history: list[dict] = []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    conversation_history.append({"role": "user", "content": message})

    response = ai.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=JOURNAL_SYSTEM_PROMPT,
        messages=conversation_history,
    )
    reply = response.content[0].text
    conversation_history.append({"role": "assistant", "content": reply})

    return jsonify({"response": reply})


@app.route("/api/extract", methods=["POST"])
def api_extract():
    """
    Close the current conversation and run extraction.

    Request body (JSON):
      date  — ISO date string for this dream, e.g. "2025-03-15"
              Defaults to today if omitted.

    Returns the extracted data and the new dream node ID.
    Prints the full extraction to stdout for terminal verification.
    """
    if not conversation_history:
        return jsonify({"error": "No conversation in progress"}), 400

    data = request.json or {}
    dream_date = data.get("date") or _date.today().isoformat()

    # Run extraction (separate Claude call, not part of the conversation)
    extracted = extract_dream(conversation_history, dream_date)

    print("\n" + "=" * 60)
    print("EXTRACTION RESULT")
    print("=" * 60)
    print(json.dumps(extracted, indent=2))
    print("=" * 60 + "\n")

    # Write to graph and save
    dream_id = write_to_graph(extracted, dg, dream_date)
    dg.save()

    print(f"Written to graph as: {dream_id}")
    print(f"Graph stats: {json.dumps(dg.stats(), indent=2)}")

    # Clear history so the next entry starts fresh
    conversation_history.clear()

    return jsonify({"dream_id": dream_id, "extracted": extracted})


@app.route("/api/dreams")
def get_dreams():
    return jsonify(dg.get_all_dreams())


if __name__ == "__main__":
    app.run(debug=True, port=5001)
