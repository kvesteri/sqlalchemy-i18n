from pytest import raises
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_i18n import Translatable, ImproperlyConfigured
from tests import TestCase


class TestPropertyCollision(TestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255))
            ]
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

    def setup_method(self, method):
        self.engine = sa.create_engine(
            'postgres://postgres@localhost/sqlalchemy_i18n_test'
        )
        self.Model = declarative_base()

        self.create_models()

    def test_raises_exception(self):
        with raises(ImproperlyConfigured):
            self.Article()

    def teardown_method(self, method):
        self.engine.dispose()
