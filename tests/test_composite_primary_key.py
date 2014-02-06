import sqlalchemy as sa
from sqlalchemy_i18n import Translatable, translation_base
from tests import TestCase


class TestCompositePrimaryKey(TestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': ['fi', 'en'],
                'auto_create_locales': True,
            }

            id1 = sa.Column(sa.Integer, primary_key=True)

            id2 = sa.Column(sa.Integer, primary_key=True)

            locale = 'en'

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation

    def test_relationships(self):
        article = self.Article(id1=1, id2=1)
        article.name = u'Some article'
        self.session.add(article)
        self.session.commit()

        assert article.name == u'Some article'
