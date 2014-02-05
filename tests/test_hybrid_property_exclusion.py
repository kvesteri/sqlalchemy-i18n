import sqlalchemy as sa
from sqlalchemy_i18n import Translatable, translation_base
from tests import TestCase


class TestHybridPropertyExclusion(TestCase):
    create_tables = False
    configure_mappers = False

    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': ['fi', 'en'],
                'auto_create_locales': True,
                'exclude_hybrid_properties': ['word_count']
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

            word_count = sa.Column(sa.Integer)

            locale = sa.Column(sa.Unicode(255), default=u'en')

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

            word_count = sa.Column(sa.Integer)

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation

    def test_does_not_generate_hybrid_properties(self):
        self.Article()
