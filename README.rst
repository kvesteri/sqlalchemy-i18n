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


.. code-block:: python


    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base

    engine = create_engine(
        'postgres://postgres@localhost/sqlalchemy_i18n'
    )
    Base = declarative_base()


You only need to define two things, first you have to make the desired mapper translatable using make_translatable() function.
Internally this function attaches two sqlalchemy event listeners for given mapper.

NOTICE: Calling make_translatable() for given mapper should happen only once per application.

.. code-block:: python


    from sqlalchemy_i18n import make_translatable

    make_translatable(sa.orm.mapper)


Secondly you need to define translatable models. In the following example we add translatable Article model with two translatable properties (name and content).


.. code-block:: python


    import sqlalchemy as sa
    from sqlalchemy_i18n import Translatable, translation_base


    class Article(Base, Translatable):
        id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
        description = sa.Column(sa.UnicodeText)


    class ArticleTranslation(translation_base(Article)):
        __tablename__ = 'article_translation'

        name = sa.Column(sa.Unicode(255))
        content = sa.Column(sa.UnicodeText)




Resources
---------

- `Documentation <https://sqlalchemy-i18n.readthedocs.io/>`_
- `Issue Tracker <http://github.com/kvesteri/sqlalchemy-i18n/issues>`_
- `Code <http://github.com/kvesteri/sqlalchemy-i18n/>`_

.. |Build Status| image:: https://travis-ci.org/kvesteri/sqlalchemy-i18n.png?branch=master
   :target: https://travis-ci.org/kvesteri/sqlalchemy-i18n
.. |Version Status| image:: https://img.shields.io/pypi/v/SQLAlchemy-i18n.svg
   :target: https://pypi.python.org/pypi/SQLAlchemy-i18n/
.. |Downloads| image:: https://img.shields.io/pypi/dm/SQLAlchemy-i18n.svg
   :target: https://pypi.python.org/pypi/SQLAlchemy-i18n/
