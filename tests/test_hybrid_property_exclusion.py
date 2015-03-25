# -*- coding: utf-8 -*-

import sqlalchemy as sa

from sqlalchemy_i18n import Translatable, translation_base
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests import ClassicBase, ClassicTestCase, DeclarativeTestCase


class Suite(object):
    create_tables = False
    configure_mappers = False

    def test_does_not_generate_hybrid_properties(self):
        self.Article()


class TestDeclarative(Suite, DeclarativeTestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': ['fi', 'en'],
                'auto_create_locales': True,
                'exclude_hybrid_properties': ['word_count']
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

            word_count = sa.Column(sa.Integer)

            locale = sa.Column(sa.Unicode(255), default=u'en')

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

            word_count = sa.Column(sa.Integer)

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation


class TestClassic(Suite, ClassicTestCase):
    def create_tables(self):
        self.article = sa.Table(
            'article', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2), default='en'),
            sa.Column('word_count', sa.Integer))
        self.article_translation = sa.Table(
            'article_translation', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('article'),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255)),
            sa.Column('content', sa.UnicodeText),
            sa.Column('word_count', sa.Integer))

    def create_models(self):
        class Article(ClassicBase, Translatable):
            __translatable__ = {
                'locales': self.locales,
                'auto_create_locales': True,
                'exclude_hybrid_properties': ['word_count'],
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

        class ArticleTranslation(ClassicBase, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation
