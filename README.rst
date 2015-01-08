SQLAlchemy-i18n
===============

|Build Status| |Version Status| |Downloads|

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


You only need to do two things, first you have to pass the supported locales to the
`make_translatable` function::

    from sqlalchemy_i18n import make_translatable

    make_translatable(options={'locales': ['fi', 'en']})


Then you need to split your model content into translatable and non translatable::

    from sqlalchemy_i18n import Translatable, translation_base

    class Article(Base, Translatable):
        __tablename__ = 'article'
        id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
        description = sa.Column(sa.UnicodeText)


    class ArticleTranslation(translation_base(Article)):
        __tablename__ = 'article_translation'

        name = sa.Column(sa.Unicode(255))
        content = sa.Column(sa.UnicodeText)



Resources
---------

- `Documentation <http://sqlalchemy-i18n.readthedocs.org/>`_
- `Issue Tracker <http://github.com/kvesteri/sqlalchemy-i18n/issues>`_
- `Code <http://github.com/kvesteri/sqlalchemy-i18n/>`_

.. |Build Status| image:: https://travis-ci.org/kvesteri/sqlalchemy-i18n.png?branch=master
   :target: https://travis-ci.org/kvesteri/sqlalchemy-i18n
.. |Version Status| image:: https://pypip.in/v/SQLAlchemy-i18n/badge.png
   :target: https://crate.io/packages/SQLAlchemy-i18n/
.. |Downloads| image:: https://pypip.in/d/SQLAlchemy-i18n/badge.png
   :target: https://crate.io/packages/SQLAlchemy-i18n/
