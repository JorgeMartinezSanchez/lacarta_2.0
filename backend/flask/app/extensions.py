from datetime import date

from flask.json.provider import DefaultJSONProvider
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _default(o):
    # Flask serializa las fechas como "Mon, 16 Nov 2026 00:00:00 GMT"; para JS
    # es más cómodo ISO 8601 ("2026-11-16"), que new Date() entiende directo.
    if isinstance(o, date):
        return o.isoformat()
    return DefaultJSONProvider.default(o)  # dataclasses (DTOs), Decimal, etc.


class JSONProvider(DefaultJSONProvider):
    ensure_ascii = False  # "Salteña" y no "Salteña"
    default = staticmethod(_default)
