"""paste - encrypted paste package.

Contents
    crypto.py  AES helper for the paste body
    store.py   create / fetch / burn / sweep helpers
    api.py     the /api/pastes and /p/<token> blueprint
    models.py  compatibility shim, see below

The SQLAlchemy handle and the Paste model are declared once, in the
PROJECT-ROOT models.py, because web/app.py, cli.py and wsgi.py need them too.
db lives in that root module, so the correct import inside this package is

    from models import db, Paste

and NOT 'from . import db', which would look for a non-existent paste/db.py.
The handle is re-exported here only so 'from paste import db' keeps working.
"""

from ..models import Paste, db

__all__ = ["Paste", "db"]
