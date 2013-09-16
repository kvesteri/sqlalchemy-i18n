import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from tests import TestCase


class TestDefaultLocaleAsCallable(TestCase):
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

            locale = sa.Column(sa.Unicode(255), default=u'en')

            def get_locale(self):
                return 'en'

        self.Article = Article

    def test_hybrid_properties_support_callable_default_locales(self):
        article = self.Article()
        article.name = u'Some article'
        assert article.name == u'Some article'
