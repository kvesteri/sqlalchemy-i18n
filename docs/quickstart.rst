QuickStart
----------


In order to make your models use SQLAlchemy-i18n you need two things:

1. Call make_translatable() before your models are defined.
2. Add __translatable__ to all models you wish to add internationalization to


::


    import sqlalchemy as sa
    from sqlalchemy_i18n import make_translatable


    make_translatable()


    class Article(Base):
        __tablename__ = 'article'
        __translated_columns__ = {
            sa.Column('name', sa.Unicode(255))
            sa.Column('content', sa.UnicodeText)
        }
        __translatable__ = {
            'locales': [u'en', u'fi']
        }
        locale = 'en'  # this defines the default locale

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

        author = sa.Column(sa.Unicode(255))



    article = Article()
    article.name = u'Some article'

    session.add(article)
    session.commit()
