import datetime

from flask import Blueprint, abort, jsonify, request

from ..models import db
from .store import burn, create_paste, get_paste

bp = Blueprint("paste", __name__)


@bp.post("/api/pastes")
def create():
    d = request.get_json(force=True, silent=True) or {}
    if not d.get("ciphertext"):
        return jsonify({"error": "ciphertext required"}), 400
    p = create_paste(
        d["ciphertext"],
        d.get("iv", ""),
        d.get("salt", ""),
        d.get("lang", "text"),
        d.get("expiry", ""),
        d.get("burn", False),
    )
    return jsonify({"token": p.token, "url": f"/p/{p.token}"})


@bp.get("/p/<token>")
def view(token):
    p = get_paste(token)
    if not p:
        abort(404)
    if p.expires_at and p.expires_at < datetime.datetime.now(datetime.UTC).replace(tzinfo=None):
        db.session.delete(p)
        db.session.commit()
        abort(410)
    p.views += 1
    if p.burn and p.views > 1:
        db.session.delete(p)
        db.session.commit()
        abort(410)
    db.session.commit()
    return jsonify(
        {
            "iv": p.iv,
            "salt": p.salt,
            "ciphertext": p.ciphertext,
            "lang": p.lang,
            "burn": bool(p.burn),
            "views": p.views,
        }
    )


@bp.delete("/p/<token>")
def delete(token):
    burn(token)
    return jsonify({"status": "burned"})
