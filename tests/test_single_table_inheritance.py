import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_i18n import Translatable
from tests import TestCase


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

    def setup_method(self, method):
        self.engine = sa.create_engine(
            'postgres://postgres@localhost/sqlalchemy_i18n_test'
        )
        self.Model = declarative_base()

        self.create_models()

    def test_model_initialization(self):
        self.Article()

    def teardown_method(self, method):
        self.engine.dispose()
