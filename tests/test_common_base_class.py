# -*- coding: utf-8 -*-

import sqlalchemy as sa

from sqlalchemy_i18n import Translatable, translation_base
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests import ClassicBase, ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_translatable_dict_copied_to_each_child_class(self):
        assert (
            self.Article.__translatable__['class'] == self.ArticleTranslation
        )
        assert (
            self.TextItem.__translatable__['class'] == self.TextItemTranslation
        )


class TestDeclarative(Suite, DeclarativeTestCase):
    def create_models(self):
        class Base(self.Model, Translatable):
            __abstract__ = True
            __translatable__ = {
                'locales': ['en', 'fi'],
            }
            locale = 'en'

        class TextItem(Base):
            __tablename__ = 'text_item'

            id = sa.Column(sa.Integer, primary_key=True)

        class TextItemTranslation(translation_base(TextItem)):
            __tablename__ = 'text_item_translation'

            name = sa.Column(sa.Unicode(255))

        class Article(Base):
            __tablename__ = 'article'
            id = sa.Column(
                sa.Integer, primary_key=True
            )

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

        self.TextItem = TextItem
        self.TextItemTranslation = TextItemTranslation
        self.Article = Article
        self.ArticleTranslation = ArticleTranslation


class TestClassic(Suite, ClassicTestCase):
    def create_tables(self):
        ClassicTestCase.create_tables(self)

        self.textitems = sa.Table(
            'textitems', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False))
        self.textitems_translation = sa.Table(
            'textitems_translation', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('textitems'),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.UnicodeText))

    def create_models(self):
        class CommonBase(ClassicBase, Translatable):
            __translatable__ = {
                'locales': self.locales
            }
            locale = 'en'

        class TextItem(CommonBase):
            __translated_columns__ = [
                sa.Column('name', sa.UnicodeText),
            ]

        class TextItemTranslation(BaseTranslationMixin):
            __parent_class__ = TextItem

        class Article(CommonBase, Translatable):
            __translated_columns__ = [
                sa.Column('content', sa.UnicodeText),
            ]

        class ArticleTranslation(BaseTranslationMixin):
            __parent_class__ = Article

        self.TextItem = TextItem
        self.TextItemTranslation = TextItemTranslation
        self.Article = Article
        self.ArticleTranslation = ArticleTranslation

    def create_mappers(self):
        sa.orm.mapper(self.TextItem, self.textitems)
        sa.orm.mapper(self.TextItemTranslation, self.textitems_translation)
        ClassicTestCase.create_mappers(self)
