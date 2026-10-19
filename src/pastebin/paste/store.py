import secrets
import string
from datetime import timedelta

from ..clock import utcnow

_ALPHABET = string.ascii_letters + string.digits


def create_paste(ciphertext, iv, salt, lang, expiry="", burn=False):
    from ..models import Paste, db

    expires = None
    if expiry in _EXPIRY:
        expires = utcnow() + timedelta(seconds=_EXPIRY[expiry])
    token = "".join(secrets.choice(_ALPHABET) for _ in range(8))
    p = Paste(
        token=token,
        iv=iv,
        salt=salt,
        ciphertext=ciphertext,
        lang=lang,
        expires_at=expires,
        burn=1 if burn else 0,
    )
    db.session.add(p)
    db.session.commit()
    return p


def get_paste(token):
    from ..models import Paste

    return Paste.query.filter_by(token=token).first()


def burn(token):
    from ..models import Paste, db

    p = Paste.query.filter_by(token=token).first()
    if p:
        db.session.delete(p)
        db.session.commit()


def sweep_expired():
    from ..models import Paste, db

    expired = Paste.query.filter(Paste.expires_at < utcnow()).all()
    for p in expired:
        db.session.delete(p)
    db.session.commit()
    return len(expired)


_EXPIRY = {"5m": 5 * 60, "1h": 3600, "1d": 86400, "7d": 7 * 86400}
