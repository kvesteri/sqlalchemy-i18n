SQLAlchemy-i18n
===============

What for?
---------

Installation
------------


    pip install SQLAlchemy-i18n


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

Several configuration options exists for SQLAlchemy-i18n. Each of these options can be set at either manager level or model level. Setting options an manager level affects all models using given translation manager where as model level configuration only affects given model.


* locales

    Defines the list of locales that given model or manager supports

* auto_create_locales

    Whether or not to auto-create all locales whenever some of the locales is created. By default this option is True. It is highly recommended to leave this as True, since not creating all locales at once can lead to problems in multithreading environments.

    Consider for example the following situtation. User creates a translatable Article which has two translatable fields (name and content). At the first request this article is created along with one translation table entry with locale 'en'.

    After this two users edit the finnish translation of this article at the same time. The application tries to create finnish translation twice resulting in database integrity errors.

* base_classes

    What base classes should the translation class use.

* table_name

    Table name template for translation tables. By default this is '%s_translation', indicating that for example the translation table name of table 'article' would be 'article_translation'.

* locale_column_name

    The name of the locale column in translation tables. By default this is 'locale'.

* default_locale

    Default locale to use. By default this is 'en'.

* get_locale_fallback


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

