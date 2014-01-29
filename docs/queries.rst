
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


Joinedload all translations
--------------------------

::

    import sqlalchemy as sa


    articles = (
        session.query(Article)
        .options(sa.orm.joinedload(Article.translations))
    )
