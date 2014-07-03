# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests.classic import Base, TestCase


class TestRelationships(TestCase):
    def create_tables(self):
        self.articles = sa.Table(
            'articles', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('content', sa.UnicodeText))
        self.categories = sa.Table(
            'categories', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('article_id', sa.Integer, sa.ForeignKey('articles.id')))
        self.categories_l10n = sa.Table(
            'categories_l10n', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('categories'),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255)))

    def create_models(self):
        class Article(Base):
            __translatable__ = {
                'locales': self.locales,
                'default_locale': 'en',
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

        class Category(Base, Translatable):
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
            ]

        class CategoryL10N(Base, BaseTranslationMixin):
            __parent_class__ = Category

        self.Article = Article
        self.Category = Category
        self.CategoryL10N = CategoryL10N

    def create_mappers(self):
        sa.orm.mapper(self.Article, self.articles)
        sa.orm.mapper(self.Category, self.categories, properties={
            'article': sa.orm.relationship(
                self.Article,
                backref=sa.orm.backref('categories',
                                       passive_deletes=True,
                                       cascade='all, delete-orphan'))
        })
        sa.orm.mapper(self.CategoryL10N, self.categories_l10n)

    def test_nullify_relation(self):
        article = self.Article()
        article.content = u'Some content'
        article.categories.append(self.Category())
        self.session.commit()
        article.categories = []
        self.session.commit()
        assert not self.session.query(self.CategoryL10N).count()
