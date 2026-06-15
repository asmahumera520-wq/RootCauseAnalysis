"""
app.py  –  Main Flask application
Run with:  python backend/app.py
"""

import os
import sys

# Make sure the backend folder is on the path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from database import init_db, save_incident, save_rca, get_all_incidents, get_incident_with_rca, delete_incident
from services.log_parser import parse_logs
from services.diff_parser import parse_git_diff
from services.prompt_builder import build_rca_prompt
from services.ai_service import generate_rca_from_prompt

# ─── App setup ────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(__file__))   # project root
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)   # allow cross-origin requests from the frontend

# ─── Serve frontend files ─────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/report')
def report():
    return send_from_directory(FRONTEND_DIR, 'report.html')


@app.route('/history')
def history():
    return send_from_directory(FRONTEND_DIR, 'history.html')


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ─── API: health check ────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "RCA Drafter is running!"})


# ─── API: generate RCA ────────────────────────────────────────────────────────

@app.route('/api/generate-rca', methods=['POST'])
def generate_rca():
    """
    Accepts a multipart/form-data POST with:
        title, severity, incident_date, affected_systems, timeline  (text fields)
        log_file  (optional file upload)
        diff_file (optional file upload)

    Returns JSON: { success, incident_id, rca }
    """
    try:
        # ── 1. Read form fields ───────────────────────────────────
        title            = request.form.get('title', '').strip()
        severity         = request.form.get('severity', 'P2').strip()
        incident_date    = request.form.get('incident_date', '').strip()
        affected_systems = request.form.get('affected_systems', '').strip()
        timeline         = request.form.get('timeline', '').strip()

        if not title or not timeline:
            return jsonify({"success": False, "error": "Title and Timeline are required."}), 400

        # ── 2. Read uploaded files ────────────────────────────────
        log_content  = ""
        diff_content = ""

        if 'log_file' in request.files:
            f = request.files['log_file']
            if f and f.filename:
                log_content = f.read().decode('utf-8', errors='ignore')

        if 'diff_file' in request.files:
            f = request.files['diff_file']
            if f and f.filename:
                diff_content = f.read().decode('utf-8', errors='ignore')

        # ── 3. Parse inputs ───────────────────────────────────────
        parsed_logs = parse_logs(log_content)
        parsed_diff = parse_git_diff(diff_content)

        # ── 4. Build AI prompt ────────────────────────────────────
        prompt = build_rca_prompt(
            title=title,
            severity=severity,
            timeline=timeline,
            affected_systems=affected_systems,
            parsed_logs=parsed_logs,
            parsed_diff=parsed_diff,
        )

        # ── 5. Call Gemini ────────────────────────────────────────
        rca_text = generate_rca_from_prompt(prompt)

        # ── 6. Persist to database ────────────────────────────────
        incident_id = save_incident(title, severity, timeline, incident_date, affected_systems)
        save_rca(incident_id, rca_text)

        # ── 7. Return result ──────────────────────────────────────
        return jsonify({
            "success":     True,
            "incident_id": incident_id,
            "rca":         rca_text,
        })

    except RuntimeError as exc:
        return jsonify({"success": False, "error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"success": False, "error": f"Unexpected error: {exc}"}), 500


# ─── API: list all incidents ──────────────────────────────────────────────────

@app.route('/api/incidents', methods=['GET'])
def list_incidents():
    return jsonify(get_all_incidents())


# ─── API: get one incident + its RCA ─────────────────────────────────────────

@app.route('/api/incidents/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    result = get_incident_with_rca(incident_id)
    if result:
        return jsonify(result)
    return jsonify({"error": "Incident not found"}), 404


# ─── API: delete an incident ──────────────────────────────────────────────────

@app.route('/api/incidents/<int:incident_id>', methods=['DELETE'])
def remove_incident(incident_id):
    delete_incident(incident_id)
    return jsonify({"success": True, "deleted_id": incident_id})


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    print("\n[RCA Drafter] Running at http://localhost:5000\n")
    app.run(debug=True, port=5000)
