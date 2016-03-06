Configuration
=============


Several configuration options exists for SQLAlchemy-i18n. Each of these options can be set at either manager level or model level. Setting options an manager level affects all models using given translation manager where as model level configuration only affects given model.


Dynamic source locale
---------------------

Sometimes you may want to have dynamic source (default) locale. This can be achieved by setting `dynamic_source_locale` as `True`.


Consider the following model definition::


    class Article(Base):
        __tablename__ = 'article'
        __translatable__ = {
            'locales': [u'en', u'fi'],
            'dynamic_source_locale': True
        }

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

        author = sa.Column(sa.Unicode(255))

        def get_locale(self):
            return 'en'


    class ArticleTranslation(translation_base(Article)):
        __tablename__ = 'article_translation'

        name = sa.Column(sa.Unicode(255))
        content = sa.Column(sa.UnicodeText)


Now you can use the dynamic source locales as follows::


    article = Article(locale='fi', name=u'Joku artikkeli')
    article.name == article.translations['fi'].name  # True

    article2 = Article(locale='en', name=u'Some article)
    article2.name == article.translations['en'].name  # True



As with regular translations, the translations using dynamic source locales can even be fetched efficiently using good old SQLAlchemy loading constructs::


    articles = (
        session.query(Article)
        .options(sa.orm.joinedload(Article.current_translation))
    )  # loads translations based on the locale in the parent class


Other options
-------------


* locales

    Defines the list of locales that given model or manager supports

* auto_create_locales

    Whether or not to auto-create all locales whenever some of the locales is created. By default this option is True. It is highly recommended to leave this as True, since not creating all locales at once can lead to problems in multithreading environments.

    Consider for example the following situtation. User creates a translatable Article which has two translatable fields (name and content). At the first request this article is created along with one translation table entry with locale 'en'.

    After this two users edit the finnish translation of this article at the same time. The application tries to create finnish translation twice resulting in database integrity errors.

* fallback_locale

    The locale which will be used as a fallback for translation hybrid properties that return None or empty string.

* translations_relationship_args

    Dictionary of arguments passed as defaults for automatically created translations relationship.::


    class Article(Base):
        __tablename__ = 'article'
        __translatable__ = {
            'locales': [u'en', u'fi'],
            'translations_relationship_args': {
                'passive_deletes': False
            }
        }

        id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

        author = sa.Column(sa.Unicode(255))

        def get_locale(self):
            return 'en'


    class ArticleTranslation(translation_base(Article)):
        __tablename__ = 'article_translation'

        name = sa.Column(sa.Unicode(255))
        content = sa.Column(sa.UnicodeText)
