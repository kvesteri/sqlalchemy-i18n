
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


Joinedloading arbitrary translations
------------------------------------

::

    import sqlalchemy as sa


    articles = (
        session.query(Article)
        .options(sa.orm.joinedload(Article.translations['fi']))
        .options(sa.orm.joinedload(Article.translations['en']))
    )
