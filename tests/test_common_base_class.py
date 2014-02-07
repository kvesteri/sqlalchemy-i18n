import sqlalchemy as sa
from sqlalchemy_i18n import Translatable, translation_base
from tests import TestCase


class TestCommonBaseClass(TestCase):
    def create_models(self):
        class Base(self.Model, Translatable):
            __abstract__ = True
            __translatable__ = {
                'locales': ['en', 'fi'],
            }
            locale = 'en'

        class TextItem(Base):
            __tablename__ = 'text_item'

            id = sa.Column(sa.Integer, primary_key=True)

        class TextItemTranslation(translation_base(TextItem)):
            __tablename__ = 'text_item_translation'

            name = sa.Column(sa.Unicode(255))

        class Article(Base):
            __tablename__ = 'article'
            id = sa.Column(
                sa.Integer, primary_key=True
            )

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

        self.TextItem = TextItem
        self.TextItemTranslation = TextItemTranslation
        self.Article = Article
        self.ArticleTranslation = ArticleTranslation

    def test_translatable_dict_copied_to_each_child_class(self):
        assert (
            self.Article.__translatable__['class'] == self.ArticleTranslation
        )
        assert (
            self.TextItem.__translatable__['class'] == self.TextItemTranslation
        )
