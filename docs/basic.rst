
Basic usage
===========

Current translation
-------------------

Current translation is a hybrid property in parent object that returns the associated translation object for current locale.::


    article = Article()
    article.current_translation.name = 'Some article'


You can also directly set the current translation::


    article.current_translation = ArticleTranslation(name='Some article')


Articles and translations can be efficiently fetched using various SQLAlchemy loading strategies::


    session.query(Article).options(joinedload(Article.current_translation))


Fallback translation
--------------------

If there is no translation available for the current locale then fallback locale is being used. Fallback translation is a convenient hybrid property
for accessing this translation object.::


    article = Article()
    article.translations.en.name = 'Some article'

    article.fallback_translation.name  # Some article


Fallback translation is especially handy in situations where you don't necessarily have all the objects translated in various languages but need to fetch them efficiently. ::


    query = (
        session.query(Article)
        .options(joinedload(Article.current_translation))
        .options(joinedload(Article.fallback_translation))
    )



Translatable columns as hybrids
-------------------------------

For each translatable column SQLAlchemy-i18n creates a hybrid property in the parent class. These hybrid properties always point at the current translation.

Example: ::


    article = Article()
    article.name = u'Some article'

    article.translations['en'].name  # u'Some article'


If the there is no translation available for current locale then these hybrids return the translation for fallback locale. Let's assume the current locale here is 'fi'::


    article = Article()
    article.translations.fi.name = ''
    article.translations.en.name = 'Some article'

    article.name  # 'Some article'



Accessing translations
----------------------

Dictionary based access::


    article.translations['en'].name = u'Some article'


Attribute access::

    article.translations.en.name = u'Some article'
    article.translations.fi.name = u'Joku artikkeli'

