# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests.classic import Base, TestCase


class TestCompositePrimaryKey(TestCase):
    def create_tables(self):
        self.articles = sa.Table(
            'articles', self.metadata,
            sa.Column('id1', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('id2', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False))
        self.articles_l10n = sa.Table(
            'articles_l10n', self.metadata,
            sa.Column('id1', sa.Integer,
                      primary_key=True,
                      nullable=False),
            sa.Column('id2', sa.Integer,
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255)),
            sa.Column('content', sa.UnicodeText),
            sa.ForeignKeyConstraint(['id1', 'id2'],
                                    ['articles.id1', 'articles.id2']))

    def create_models(self):
        class Article(Base, Translatable):
            __translatable__ = {
                'locales': self.locales
            }
            __translated_columns__ = [
                sa.Column('content', sa.UnicodeText),
            ]
            locale = 'en'

        class ArticleL10N(Base, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleL10N = ArticleL10N

    def test_relationships(self):
        article = self.Article(id1=1, id2=1)
        article.name = u'Some article'
        self.session.add(article)
        self.session.commit()

        assert article.name == u'Some article'
