
Queries
=======

Joinedload current translation
------------------------------

::


    import sqlalchemy as sa


    articles = (
        session.query(Article)
        .options(sa.orm.joinedload(Article.current_translation))
    )

    print articles[0].name


Joinedload arbitrary translations
---------------------------------

::

    import sqlalchemy as sa


    articles = (
        session.query(Article)
        .options(sa.orm.joinedload(Article.translations['fi']))
        .options(sa.orm.joinedload(Article.translations['en']))
    )


You can also use attribute accessors::


    articles = (
        session.query(Article)
        .options(sa.orm.joinedload(Article.translations.fi))
        .options(sa.orm.joinedload(Article.translations.en))
    )


Joinedload all translations
---------------------------

::


    articles = (
        session.query(Article)
        .options(sa.orm.joinedload(Article.translations))
    )
