import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from tests import TestCase


class TestAbstractBaseClassWithColumns(TestCase):
    def create_models(self):
        class TranslationBase(self.Model):
            __abstract__ = True
            content = sa.Column(sa.UnicodeText)

        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'base_classes': (TranslationBase, ),
                'locales': ['en', 'fi']
            }

            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255))
            ]
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

        self.Article = Article

    def test_inherits_column_from_abstract_base_class(self):
        class_ = self.Article.__translatable__['class']
        assert class_.__name__ == 'ArticleTranslation'
