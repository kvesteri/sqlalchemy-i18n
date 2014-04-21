QuickStart
----------


In order to make your models use SQLAlchemy-i18n you need two things:

1. Call make_translatable() before your models are defined.
2. Define translation model and make it inherit mixin provided by translation_base function


::


    import sqlalchemy as sa
    from sqlalchemy_i18n import make_translatable, translation_base


    make_translatable()


    class Article(Base):
        __tablename__ = 'article'
        __translatable__ = {
            'locales': ['en', 'fi']
        }
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
