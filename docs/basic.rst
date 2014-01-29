
Basic usage
===========

Translatable columns as hybrids
-------------------------------

For each translatable column SQLAlchemy-i18n creates a hybrid property in the parent class. These hybrid properties always point at the current translation.

Example: ::


    article = Article()
    article.name = u'Some article'

    article.translations['en'].name  # u'Some article'


Accessing translations
----------------------

::


    article = Article()
    article.translations['en'].name = u'Some article'
    session.add(article)
    session.commit()


Using force_locale
------------------

You can force your models to use custom current locale by using force_locale context managers.


::


    article = Article()

    article.translations['fi'].name = u'Joku artikkeli'
    article.translations['en'].name = u'Some article'


    article.name  # u'Some article'

    with article.force_locale('fi'):
        article.name  # u'Joku artikkeli'



Callables as default locale
---------------------------
