from pytest import raises
import sqlalchemy as sa
from sqlalchemy_i18n import (
    Translatable, translation_base, ImproperlyConfigured
)
from tests import TestCase


class TestPropertyCollision(TestCase):
    configure_mappers = False
    create_tables = False

    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'base_classes': (self.Model, ),
                'locales': ['fi', 'en'],
                'auto_create_locales': True,
                'default_locale': lambda self: self.locale or 'en'
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

            name = sa.Column(sa.Unicode(255))

            locale = sa.Column(sa.Unicode(255), default=u'en')

            def get_locale(self):
                return 'en'

        self.Article = Article

    def test_raises_exception(self):
        with raises(ImproperlyConfigured):
            class ArticleTranslation(translation_base(self.Article)):
                __tablename__ = 'article_translation'

                name = sa.Column(sa.Unicode(255))
            self.Article()


class TestPropertyCollisionWithSingleTableInheritance(TestCase):
    def create_models(self):
        class TextItem(self.Model, Translatable):
            __tablename__ = 'article'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255))
            ]

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

            def get_locale(self):
                return 'en'

        class Article(TextItem):
            description = sa.Column(sa.UnicodeText)

        self.TextItem = TextItem
        self.Article = Article

    def test_model_initialization(self):
        self.Article()
