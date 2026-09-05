from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import sys

app = Flask(__name__)

CORS(app, origins=["https://chillwaste.github.io"])

@app.route("/generate", methods=["POST"])
def generate():
    result = subprocess.run(
        [sys.executable, "your_safe_script.py"],
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        return jsonify({
            "error": result.stderr or "Script failed"
        }), 500

    return jsonify({
        "result": result.stdout
    })

app.run(host="0.0.0.0", port=5000)