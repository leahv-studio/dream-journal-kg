import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__, template_folder=FRONTEND_DIR)
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    return jsonify({"response": "hello"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
