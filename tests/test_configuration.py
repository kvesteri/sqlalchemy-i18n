import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from tests import TestCase


class TestWithoutBaseClassesOption(TestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'text_item'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText)
            ]
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)
            discriminator = sa.Column(
                sa.Unicode(100)
            )
            __mapper_args__ = {
                'polymorphic_on': discriminator,
            }

            def get_locale(self):
                pass

        self.Article = Article

    def test_generates_translation_model(self):
        assert self.Article


class TestGetLocaleFallback(TestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'text_item'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText)
            ]
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)
            discriminator = sa.Column(
                sa.Unicode(100)
            )
            __mapper_args__ = {
                'polymorphic_on': discriminator,
            }

            def get_locale(self):
                pass

        self.Article = Article

    def test_returns_default_locale_when_true(self):
        self.Article.__translatable__['default_locale'] = 'fi'
        self.Article.__translatable__['get_locale_fallback'] = True
        assert self.Article()._get_locale() == 'fi'
