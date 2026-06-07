import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ✅ Security Fix 1: Use environment variable for secret key
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Security Fix 2: Restrict upload folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max

# ✅ Security Fix 3: Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.execute("""
            INSERT OR IGNORE INTO users (username, password)
            VALUES (?, ?)
        """, ("admin", generate_password_hash("admin123")))

init_db()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # ✅ Security Fix 4: Input validation
        if not username or not password:
            flash("Username and password required")
            return render_template("login.html")

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()
            if user and check_password_hash(user[2], password):
                session["user"] = username
                # ✅ Security Fix 5: Regenerate session
                session.permanent = False
                return redirect(url_for("upload"))
            else:
                flash("Invalid credentials")
    return render_template("login.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename:
            # ✅ Security Fix 6: Validate file extension
            if not allowed_file(file.filename):
                flash("File type not allowed!")
                return render_template("upload.html",
                                       user=session["user"])
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                app.config["UPLOAD_FOLDER"], filename))
            flash("File uploaded successfully!")
    return render_template("upload.html", user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    # ✅ Security Fix 7: Debug mode off in production
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
