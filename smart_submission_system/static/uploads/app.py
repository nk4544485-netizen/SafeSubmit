from flask import Flask, request, render_template, jsonify
import sqlite3
import os
import re
import hashlib
from datetime import datetime
import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

# ------------------------
# Database Setup
# ------------------------

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            submission_type TEXT,
            description TEXT,
            file_name TEXT,
            file_hash TEXT,
            text_hash TEXT,
            trust_score INTEGER,
            status TEXT,
            rejection_reason TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ------------------------
# Utility Functions
# ------------------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_file(file_path):
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()


def contains_suspicious_words(text):
    suspicious = ["asdf", "test", "dummy", "lorem", "xxx"]
    for word in suspicious:
        if word in text.lower():
            return True
    return False


def excessive_repetition(text):
    words = text.lower().split()
    if not words:
        return False
    most_common = max(set(words), key=words.count)
    return words.count(most_common) > len(words) * 0.3


def is_duplicate(text_hash, file_hash):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM submissions
        WHERE text_hash = ? OR file_hash = ?
    """, (text_hash, file_hash))
    row = cursor.fetchone()
    conn.close()
    return row is not None


# ------------------------
# Trust Score Engine
# ------------------------

def calculate_trust_score(email, description, file_present, valid_file):
    score = 0

    if validate_email(email):
        score += 10

    if len(description) > 300:
        score += 10

    if not contains_suspicious_words(description):
        score += 10

    if not excessive_repetition(description):
        score += 15

    if file_present:
        score += 10

    if valid_file:
        score += 10

    return score


def evaluate_submission(name, email, submission_type, description, file_path=None):
    if not name or not email or not submission_type or not description:
        return "Rejected", "All fields are required", 20

    if not validate_email(email):
        return "Rejected", "Invalid email format", 25

    if len(description) < 100:
        return "Rejected", "Description too short", 30

    text_hash = hash_text(description)

    file_hash = None
    file_present = False
    valid_file = False

    if file_path:
        file_present = True
        file_hash = hash_file(file_path)
        valid_file = True

    if is_duplicate(text_hash, file_hash):
        return "Rejected", "Duplicate submission detected", 10

    trust_score = calculate_trust_score(
        email, description, file_present, valid_file
    )

    if trust_score >= 80:
        status = "Accepted"
        reason = "Submission verified successfully"
    elif trust_score >= 50:
        status = "Flagged"
        reason = "Submission needs manual review"
    else:
        status = "Rejected"
        reason = "Low trust score"

    return status, reason, trust_score


# ------------------------
# Routes
# ------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit_form():
    name = request.form.get("name")
    email = request.form.get("email")
    submission_type = request.form.get("submission_type")
    description = request.form.get("description")
    file = request.files.get("file")

    file_name = None
    file_path = None

    if file and file.filename:
        if not allowed_file(file.filename):
            return render_template(
                "result.html",
                name=name,
                status="Rejected",
                reason="Invalid file type",
                trust_score=0
            )

        file_name = file.filename
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
        file.save(file_path)

    status, reason, trust_score = evaluate_submission(
        name, email, submission_type, description, file_path
    )

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO submissions
        (name, email, submission_type, description, file_name,
         file_hash, text_hash, trust_score, status, rejection_reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        email,
        submission_type,
        description,
        file_name,
        hash_file(file_path) if file_path else None,
        hash_text(description),
        trust_score,
        status,
        reason,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        name=name,
        status=status,
        reason=reason,
        trust_score=trust_score
    )


@app.route("/api/submit", methods=["POST"])
def submit_api():
    data = request.form or request.json

    name = data.get("name")
    email = data.get("email")
    submission_type = data.get("submission_type")
    description = data.get("description")

    file = request.files.get("file")

    file_name = None
    file_path = None

    if file and file.filename:
        if not allowed_file(file.filename):
            return jsonify({
                "status": "Rejected",
                "reason": "Invalid file type",
                "trust_score": 0
            }), 400

        file_name = file.filename
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
        file.save(file_path)

    status, reason, trust_score = evaluate_submission(
        name, email, submission_type, description, file_path
    )

    return jsonify({
        "name": name,
        "status": status,
        "reason": reason,
        "trust_score": trust_score
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
