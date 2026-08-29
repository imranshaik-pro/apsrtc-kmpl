#!/usr/bin/env python3
"""
Flask server to generate reports on-demand via HTTP.
"""

import os
import sys
import subprocess
import json
import re
from flask import Flask, request, jsonify

app = Flask(__name__)
PROJECT_DIR = "/home/imran/apsrtc-kmpl"
GDRIVE_FOLDER = "1tU9aw7Cdw-Q-7mr9BMhayORKMy61_DOz"

def upload_to_drive(file_path):
    cmd = ["gdrive", "files", "upload", "--parent", GDRIVE_FOLDER, file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Upload failed: {result.stderr}")
    match = re.search(r"ViewUrl: (https://drive\.google\.com/file/d/[^\s]+)", result.stdout)
    if match:
        return match.group(1)
    return "Uploaded (link not found)"

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    depot = data.get('depot')
    report_date = data.get('date')
    if not depot or not report_date:
        return jsonify({"error": "Missing 'depot' or 'date'"}), 400

    # Run the report generator
    cmd = [
        "python", os.path.join(PROJECT_DIR, "generate_report.py"),
        "--depot", depot,
        "--date", report_date
    ]
    result = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True)

    if result.returncode != 0:
        error_msg = result.stderr[:200] if result.stderr else "Unknown error"
        return jsonify({"error": error_msg}), 500

    # Find the generated file
    match = re.search(r"Saved to: (reports/[^\s]+)", result.stdout)
    if not match:
        return jsonify({"error": "File not found in output"}), 500

    file_path = os.path.join(PROJECT_DIR, match.group(1))
    if not os.path.exists(file_path):
        return jsonify({"error": "File missing on disk"}), 500

    # Upload to Drive
    try:
        drive_link = upload_to_drive(file_path)
        return jsonify({"status": "success", "drive_link": drive_link})
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
