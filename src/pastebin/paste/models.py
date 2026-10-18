"""Compatibility shim - the real Paste model lives in the project-root models.py.

Every module in this project imports the model from the root module
('from models import Paste'). This file exists so that external callers
written against the old package-relative path ('from paste.models import
Paste') keep working; it forwards to the single declaration instead of
defining a second model bound to a different SQLAlchemy metadata object.
"""

from ..models import Paste, db

__all__ = ["Paste", "db"]
