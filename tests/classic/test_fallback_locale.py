# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests.classic import Base, TestCase


class LocaleFallbackTestCase(TestCase):
    def test_hybrid_properties_support_callable_fallback_locales(self):
        article = self.Article(locale=u'en')
        article.name = u'Some article'
        assert article.name == u'Some article'

    def test_locale_fallback(self):
        article = self.Article(locale=u'en')
        article.name


class TestDefaultLocaleAsCallable(LocaleFallbackTestCase):
    def create_tables(self):
        self.articles = sa.Table(
            'articles', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2), default='en'))
        self.articles_l10n = sa.Table(
            'articles_l10n', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('articles'),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255)),
            sa.Column('content', sa.UnicodeText))

    def create_models(self):
        class Article(Base, Translatable):
            __translatable__ = {
                'locales': self.locales,
                'auto_create_locales': True,
                'fallback_locale': lambda self: self.locale or 'en'
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

        class ArticleL10N(Base, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleL10N = ArticleL10N


class TestWithoutClassDefaultLocale(TestDefaultLocaleAsCallable):
    def create_models(self):
        class Article(Base, Translatable):
            __translatable__ = {
                'locales': self.locales,
                'auto_create_locales': True,
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

            def get_locale(self):
                return 'en'

        class ArticleL10N(Base, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleL10N = ArticleL10N
