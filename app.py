"""
COMSATS University Islamabad, Attock Campus
Department of Computer Science
DevOps for Cloud Computing (CSC418) - Lab Mid Project

Assignment Submission Portal
"""

from flask import Flask, request, jsonify, render_template
from urllib.parse import urlparse
import datetime
import re

app = Flask(__name__)

# In-memory storage for assignment submissions
submissions = []


def is_valid_url(url: str) -> bool:
    """Validate that the given string is a valid HTTP or HTTPS URL."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    try:
        parsed = urlparse(url)
        # Must have scheme http or https and netloc with valid domain structure
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            return False
        # Disallow simple non-domain strings like "not-a-url" or "ftp://xyz"
        if '.' not in parsed.netloc and parsed.netloc not in ('localhost', '127.0.0.1'):
            return False
        return True
    except Exception:
        return False


def validate_submission_payload(data: dict):
    """
    Validates submission data.
    Returns (is_valid: bool, error_message: str or None)
    """
    if not isinstance(data, dict):
        return False, "Invalid payload format. Expected JSON object."

    name = str(data.get("student_name", "")).strip()
    reg_no = str(data.get("reg_no", "")).strip()
    title = str(data.get("assignment_title", "")).strip()
    url = str(data.get("submission_url", "")).strip()

    if not name:
        return False, "Student name is required."

    if not reg_no:
        return False, "Missing registration number. Registration number is required."

    if not title:
        return False, "Assignment title is required."

    if not url:
        return False, "Submission URL is required."

    if not is_valid_url(url):
        return False, "Invalid submission URL. Must be a valid HTTP or HTTPS URL."

    return True, None


@app.route("/")
def index():
    """Render the web portal homepage."""
    return render_template("index.html")


@app.route("/api/submissions", methods=["GET"])
def get_submissions():
    """Retrieve all saved submissions."""
    return jsonify({
        "status": "success",
        "count": len(submissions),
        "submissions": submissions
    }), 200


@app.route("/api/submissions", methods=["POST"])
def submit_assignment():
    """
    Validate and save a student's assignment submission.
    Accepts both JSON and form data.
    """
    payload = request.get_json(silent=True) or request.form.to_dict()

    is_valid, error_msg = validate_submission_payload(payload)
    if not is_valid:
        return jsonify({
            "status": "error",
            "message": error_msg
        }), 400

    new_submission = {
        "id": len(submissions) + 1,
        "student_name": payload.get("student_name").strip(),
        "reg_no": payload.get("reg_no").strip(),
        "assignment_title": payload.get("assignment_title").strip(),
        "submission_url": payload.get("submission_url").strip(),
        "submitted_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    submissions.append(new_submission)

    return jsonify({
        "status": "success",
        "message": "The submission is saved and appears in the submission list.",
        "submission": new_submission
    }), 201


@app.route("/api/submissions/reset", methods=["POST"])
def reset_submissions():
    """Helper endpoint to reset storage during testing."""
    submissions.clear()
    return jsonify({"status": "cleared", "count": 0}), 200


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for automated probes."""
    return jsonify({"status": "healthy", "service": "Assignment Submission Portal"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

