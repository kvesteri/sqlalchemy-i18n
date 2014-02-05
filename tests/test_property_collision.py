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
                'locales': ['fi', 'en'],
                'auto_create_locales': True,
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
