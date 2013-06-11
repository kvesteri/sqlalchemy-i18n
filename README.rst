SQLAlchemy-i18n
===============

Internationalization extension for SQLAlchemy models.


Features
--------

- Stores translations in separate tables.
- Reflects translation table structures based on parent model table structure.
- Supports forcing of given locale.
- Good performance (uses proxy dicts and other advanced SQLAlchemy concepts for performance optimization)


Basic Usage
-----------

Consider you have already defined SQLAlchemy connections and declarative base as follows:


::

    import sqlalchemy as sa
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base

    engine = create_engine(
        'postgres://postgres@localhost/sqlalchemy_i18n'
    )
    Base = declarative_base()



::

    class Article(Base, Translatable):
        __translated_columns__ = [
            sa.Column('name', sa.Unicode(255)),
            sa.Column('content', sa.UnicodeText)
        ]

        id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

        description = sa.Column(sa.UnicodeText)



Resources
---------

- `Documentation <http://sqlalchemy-i18n.readthedocs.org/>`_
- `Issue Tracker <http://github.com/kvesteri/sqlalchemy-i18n/issues>`_
- `Code <http://github.com/kvesteri/sqlalchemy-i18n/>`_
