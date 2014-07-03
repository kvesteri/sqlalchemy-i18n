# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests.classic import Base, TestCase


class TestHybridPropertyExclusion(TestCase):
    create_tables = False
    configure_mappers = False

    def create_tables(self):
        self.articles = sa.Table(
            'articles', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2), default='en'),
            sa.Column('word_count', sa.Integer))
        self.articles_l10n = sa.Table(
            'articles_l10n', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('articles'),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255)),
            sa.Column('content', sa.UnicodeText),
            sa.Column('word_count', sa.Integer))

    def create_models(self):
        class Article(Base, Translatable):
            __translatable__ = {
                'locales': self.locales,
                'auto_create_locales': True,
                'exclude_hybrid_properties': ['word_count'],
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

        class ArticleL10N(Base, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleL10N = ArticleL10N

    def test_does_not_generate_hybrid_properties(self):
        self.Article()
