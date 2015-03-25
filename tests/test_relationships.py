# -*- coding: utf-8 -*-

import sqlalchemy as sa

from sqlalchemy_i18n import Translatable, translation_base
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests import ClassicBase, ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_nullify_relation(self):
        self.CategoryTranslation = self.Category.__translatable__['class']
        article = self.Article()
        article.content = u'Some content'
        article.categories.append(self.Category())
        self.session.commit()
        article.categories = []
        self.session.commit()
        assert not self.session.query(self.CategoryTranslation).count()


class TestDeclarative(Suite, DeclarativeTestCase):
    def create_models(self):
        class Article(self.Model):
            __tablename__ = 'article'
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            content = sa.Column(sa.UnicodeText)

        class Category(self.Model, Translatable):
            __tablename__ = 'category'
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            article_id = sa.Column(sa.Integer, sa.ForeignKey(Article.id))
            article = sa.orm.relationship(
                Article,
                backref=sa.orm.backref(
                    'categories',
                    passive_deletes=True,
                    cascade='all, delete-orphan'
                )
            )

        class CategoryTranslation(translation_base(Category)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

        self.Article = Article
        self.Category = Category


class TestClassic(Suite, ClassicTestCase):
    def create_tables(self):
        self.article = sa.Table(
            'article', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('content', sa.UnicodeText))
        self.category = sa.Table(
            'category', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('article_id', sa.Integer, sa.ForeignKey('article.id')))
        self.category_translation = sa.Table(
            'category_translation', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('category'),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255)))

    def create_models(self):
        class Article(ClassicBase):
            __translatable__ = {
                'locales': self.locales,
                'default_locale': 'en',
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

        class Category(ClassicBase, Translatable):
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
            ]

        class CategoryTranslation(ClassicBase, BaseTranslationMixin):
            __parent_class__ = Category

        self.Article = Article
        self.Category = Category
        self.CategoryTranslation = CategoryTranslation

    def create_mappers(self):
        sa.orm.mapper(self.Article, self.article)
        sa.orm.mapper(self.Category, self.category, properties={
            'article': sa.orm.relationship(
                self.Article,
                backref=sa.orm.backref('categories',
                                       passive_deletes=True,
                                       cascade='all, delete-orphan'))
        })
        sa.orm.mapper(self.CategoryTranslation, self.category_translation)

    def test_nullify_relation(self):
        article = self.Article()
        article.content = u'Some content'
        article.categories.append(self.Category())
        self.session.commit()
        article.categories = []
        self.session.commit()
        assert not self.session.query(self.CategoryTranslation).count()
