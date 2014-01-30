import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_i18n import Translatable
from tests import TestCase


class TestDynamicSourceLocale(TestCase):
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
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText)
            ]
            __translatable__ = {
                'base_classes': (self.Model, ),
                'locales': self.locales,
                'default_locale': 'en',
            }

            @hybrid_property
            def locale(self):
                return self._locale or 'en'

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)
            _locale = sa.Column(sa.Unicode(10), default=u'en')

        self.Article = Article

    def test_joinedload_for_current_translation(self):
        count = self.connection.query_count
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.current_translation))
        ).first()
        article.translations['en']

        assert self.connection.query_count == count + 1
