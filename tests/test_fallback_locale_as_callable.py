# -*- coding: utf-8 -*-

import sqlalchemy as sa

from sqlalchemy_i18n import Translatable, translation_base
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests import ClassicBase, ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_hybrid_properties_support_callable_fallback_locales(self):
        article = self.Article(locale=u'en')
        article.name = u'Some article'
        assert article.name == u'Some article'

    def test_locale_fallback(self):
        article = self.Article(locale=u'en')
        article.name


class TestDeclarative(Suite, DeclarativeTestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': self.locales,
                'auto_create_locales': True,
                'fallback_locale': lambda self: self.locale or 'en'
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            locale = sa.Column(sa.Unicode(255), default=u'en')

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

        self.Article = Article


class TestClassic(Suite, ClassicTestCase):
    def create_tables(self):
        self.article = sa.Table(
            'article', self.metadata,
            sa.Column(
                'id',
                sa.Integer,
                autoincrement=True,
                primary_key=True,
                nullable=False
            ),
            sa.Column('locale', sa.types.CHAR(2), default='en'))
        self.article_translation = sa.Table(
            'article_translation', self.metadata,
            sa.Column(
                'id',
                sa.Integer,
                sa.ForeignKey('article'),
                primary_key=True,
                nullable=False
            ),
            sa.Column(
                'locale',
                sa.types.CHAR(2),
                primary_key=True,
                nullable=False
            ),
            sa.Column('name', sa.Unicode(255)),
            sa.Column('content', sa.UnicodeText)
        )

    def create_models(self):
        class Article(ClassicBase, Translatable):
            __translatable__ = {
                'locales': self.locales,
                'auto_create_locales': True,
                'fallback_locale': lambda self: self.locale or 'en'
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

        class ArticleTranslation(ClassicBase, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation
