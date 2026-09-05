from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import sys

app = Flask(__name__)

CORS(app, origins=["https://chillwaste.github.io"])


@app.route("/generate", methods=["POST"])
def generate():
    try:
        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            print("main.py failed:")
            print(result.stderr)

            return jsonify({
                "error": result.stderr or "main.py failed"
            }), 500

        print("main.py output:")
        print(result.stdout)

        return jsonify({
            "result": result.stdout
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "error": "main.py timed out after 120 seconds"
        }), 500

    except Exception as e:
        print("Server error:", e)

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)