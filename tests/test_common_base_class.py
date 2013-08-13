import sqlalchemy as sa
from sqlalchemy_i18n import Translatable as _Translatable
from tests import TestCase


class TestCommonBaseClass(TestCase):
    def create_models(self):
        class Translatable(_Translatable):
            __translatable__ = {
                'base_classes': (self.Model, ),
                'locales': ['en']
            }

            def get_locale(self):
                return 'en'

        class TextItem(self.Model, Translatable):
            __tablename__ = 'text_item'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255))
            ]
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255))
            ]
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

        self.TextItem = TextItem
        self.Article = Article

    def test_each_class_has_distinct_translation_class(self):
        class_ = self.TextItem.__translatable__['class']
        assert class_.__name__ == 'TextItemTranslation'
        class_ = self.Article.__translatable__['class']
        assert class_.__name__ == 'ArticleTranslation'
