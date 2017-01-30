# -*- coding: utf-8 -*-

import sqlalchemy as sa

from sqlalchemy_i18n import Translatable, translation_base
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests import ClassicBase, ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_relationships(self):
        article = self.Article(id1=1, id2=1)
        article.name = u'Some article'
        self.session.add(article)
        self.session.commit()

        assert article.name == u'Some article'


class TestDeclarative(Suite, DeclarativeTestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': ['fi', 'en'],
                'auto_create_locales': True,
            }

            id1 = sa.Column(sa.Integer, primary_key=True)

            id2 = sa.Column(sa.Integer, primary_key=True)

            locale = 'en'

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation


class TestClassic(Suite, ClassicTestCase):
    def create_tables(self):
        self.article = sa.Table(
            'article',
            self.metadata,
            sa.Column(
                'id1',
                sa.Integer,
                primary_key=True,
                nullable=False
            ),
            sa.Column(
                'id2',
                sa.Integer,
                primary_key=True,
                nullable=False
            )
        )
        self.article_translation = sa.Table(
            'article_translation',
            self.metadata,
            sa.Column(
                'id1',
                sa.Integer,
                primary_key=True,
                nullable=False
            ),
            sa.Column(
                'id2',
                sa.Integer,
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
            sa.Column('content', sa.UnicodeText),
            sa.ForeignKeyConstraint(
                ['id1', 'id2'],
                ['article.id1', 'article.id2']
            )
        )

    def create_models(self):
        class Article(ClassicBase, Translatable):
            __translatable__ = {
                'locales': self.locales
            }
            __translated_columns__ = [
                sa.Column('content', sa.UnicodeText),
            ]
            locale = 'en'

        class ArticleTranslation(ClassicBase, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation
