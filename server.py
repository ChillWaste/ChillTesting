from flask import Flask, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    result = subprocess.run(
        ["python", "main.py"],
        capture_output=True,
        text=True,
        timeout=120
    )

    output = result.stdout

    link = re.search(r"Activation link:\s*(\S+)", output)
    code = re.search(r"Activation code:\s*(\S+)", output)
    expiry = re.search(r"Your evaluation will expire.*", output)

    return jsonify({
        "link": link.group(1) if link else None,
        "code": code.group(1) if code else None,
        "expiry": expiry.group(0) if expiry else None
    })

app.run(host="0.0.0.0", port=5000)