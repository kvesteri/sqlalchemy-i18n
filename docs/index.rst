SQLAlchemy-i18n
===============

What for?
---------

Installation
------------

QuickStart
----------

Basic usage
===========

Accessing translations
----------------------

Using force_locale
------------------

You can force your models to use custom current locale by using force_locale context managers.


::


    article = Article()

    article.translations['fi'].name = u'Joku artikkeli'
    article.translations['en'].name = u'Some article'


    with article.force_locale('fi'):
        print article.name  # 'Joku artikkeli'



Callables as default locale
---------------------------


Configuration
=============



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

