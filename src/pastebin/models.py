from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Paste(db.Model):
    __tablename__ = "pastes"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(16), unique=True)
    iv = db.Column(db.String(64), default="")
    salt = db.Column(db.String(64), default="")
    ciphertext = db.Column(db.Text, default="")
    lang = db.Column(db.String(32), default="text")
    expires_at = db.Column(db.DateTime, nullable=True)
    burn = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
