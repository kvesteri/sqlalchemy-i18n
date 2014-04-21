import sqlalchemy as sa
from sqlalchemy_i18n import Translatable, translation_base
from tests import TestCase


class LocaleFallbackTestCase(TestCase):
    def test_hybrid_properties_support_callable_fallback_locales(self):
        article = self.Article(locale=u'en')
        article.name = u'Some article'
        assert article.name == u'Some article'

    def test_locale_fallback(self):
        article = self.Article(locale=u'en')
        article.name


class TestDefaultLocaleAsCallable(LocaleFallbackTestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': ['fi', 'en'],
                'auto_create_locales': True,
                'fallback_locale': lambda self: self.locale or 'en'
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

            locale = sa.Column(sa.Unicode(255), default=u'en')

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

        self.Article = Article


class TestWithoutClassDefaultLocale(LocaleFallbackTestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': ['fi', 'en'],
                'auto_create_locales': True,
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

            locale = sa.Column(sa.Unicode(255), default=u'en')

            def get_locale(self):
                return 'en'

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

        self.Article = Article
