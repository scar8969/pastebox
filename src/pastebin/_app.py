"""b4_pastebin — Flask application entry point.

Templates live in the project-root templates/ directory, not under web/, so the
template folder is passed explicitly; Flask(__name__) alone would look in
web/templates/ and raise TemplateNotFound on "/".
The SQLite file also lives in the project-root instance/ directory.

The browser pages are a thin shell over the same functions the JSON API and the
CLI use: paste.crypto (PBKDF2-HMAC-SHA256 + AES-256-GCM) and paste.store.
"""
from datetime import datetime

from .models import Paste, db
from .paste.api import bp
from .paste.crypto import decrypt, encrypt
from .paste.store import _EXPIRY, create_paste, get_paste

from flask import Flask, jsonify, redirect, render_template, request, url_for
from . import paths

paths.ensure_runtime_dirs()

def build_app():
    """Build the application: configuration, database, then routes."""
    app = Flask(__name__, template_folder=str(paths.TEMPLATES_DIR),
                instance_path=str(paths.INSTANCE_DIR))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(paths.INSTANCE_DIR / "pastebin.db")
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(bp)

    @app.get("/")
    def index():
        return render_template("index.html",
                               pastes=Paste.query.order_by(Paste.id.desc()).limit(20).all(),
                               expiry_choices=list(_EXPIRY.keys()),
                               languages=["text", "python", "json", "bash", "sql"])

    @app.post("/create")
    def create_page():
        """Encrypt the submitted plaintext with the submitted password and store it."""
        content = request.form.get("content", "")
        password = request.form.get("password", "")
        if not content or not password:
            return redirect(url_for("index"))
        iv, salt, ct = encrypt(content, password)
        paste = create_paste(ct, iv, salt, request.form.get("lang", "text"),
                             request.form.get("expiry", ""),
                             bool(request.form.get("burn")))
        return redirect(url_for("view_page", token=paste.token))

    @app.route("/view/<token>", methods=["GET", "POST"])
    def view_page(token):
        """Human-readable page for a paste (the JSON payload is GET /p/<token>)."""
        paste = get_paste(token)
        plaintext, error = None, None
        if paste is None:
            error = "No paste is stored under this token."
        elif paste.expires_at and paste.expires_at < datetime.utcnow():
            error = "This paste has expired."
        elif request.method == "POST":
            try:
                plaintext = decrypt(paste.ciphertext, paste.iv, paste.salt,
                                    request.form.get("password", ""))
                paste.views += 1
                db.session.commit()
            except ValueError as exc:
                error = str(exc)
        return render_template("view.html", token=token, paste=paste,
                               plaintext=plaintext, error=error)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "pastes": Paste.query.count()})

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)

    return app

app = build_app()
