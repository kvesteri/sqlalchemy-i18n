from pytest import raises
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_i18n import Translatable, translation_base, UnknownLocaleError
from tests import TestCase


class TestHybridPropertyAsDynamicSourceLocale(TestCase):
    def setup_method(self, method):
        TestCase.setup_method(self, method)
        self.ArticleTranslation = self.Article.__translatable__['class']

        article = self.Article(
            description=u'Some desription',
            name=u'Some name'
        )
        self.session.add(article)
        self.session.commit()

    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': self.locales
            }

            @hybrid_property
            def locale(self):
                return self._locale or 'en'

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)
            _locale = sa.Column(sa.Unicode(10), default=u'en')


        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

            content = sa.Column(sa.UnicodeText)

        self.Article = Article

    def test_joinedload_for_current_translation(self):
        count = self.connection.query_count
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.current_translation))
        ).first()
        article.translations['en']

        assert self.connection.query_count == count + 1


class TestColumnAsDynamicSourceLocale(TestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': self.locales
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)
            locale = sa.Column(sa.Unicode(10), default=u'en')

            def __repr__(self):
                return 'Article(%r)' % self.name

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

            content = sa.Column(sa.UnicodeText)

        self.Article = Article

    def test_current_translation_when_locale_not_set(self):
        with raises(UnknownLocaleError):
            article = self.Article(name='some article')
