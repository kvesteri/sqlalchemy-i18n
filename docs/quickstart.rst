QuickStart
----------


In order to make your models use SQLAlchemy-i18n you need two things:

1. Assign get_locale function sqlalchemy_utils.i18n module. The following example shows how to do this using flask.ext.babel::


    import sqlalchemy_utils
    from flask.ext.babel import get_locale


    sqlalchemy_utils.i18n.get_locale = get_locale



2. Call make_translatable() before your models are defined.
3. Define translation model and make it inherit mixin provided by translation_base function


::


    import sqlalchemy as sa

    from sqlalchemy_i18n import (
        make_translatable,
        translation_base,
        Translatable,
    )


    make_translatable(options={'locales': ['fi', 'en']})


    class Article(Translatable, Base):
        __tablename__ = 'article'
        __translatable__ = {'locales': ['fi', 'en']}

        locale = 'en'  # this defines the default locale

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
        author = sa.Column(sa.Unicode(255))


    class ArticleTranslation(translation_base(Article)):
        __tablename__ = 'article_translation'

        name = sa.Column(sa.Unicode(255))

        content = sa.Column(sa.UnicodeText)


    article = Article()
    article.name = u'Some article'

    session.add(article)
    session.commit()
