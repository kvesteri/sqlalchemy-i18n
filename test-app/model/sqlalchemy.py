import sqlalchemy_utils
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_i18n import make_translatable
from flask_babel import get_locale, Babel


db = SQLAlchemy()
make_translatable(
    db.mapper,
    options={
        "locales": ["ja", "en"],
        "fallback_locale": "en",
        "auto_create_locales": False,
        "fallback_to_parent": True
    },
)

babel = Babel()

sqlalchemy_utils.i18n.get_locale = get_locale
