# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_i18n import Translatable, translation_manager
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests.classic import Base, TestCase

class TestCommonBaseClass(TestCase):
    def create_tables(self):
        TestCase.create_tables(self)

        self.textitems = sa.Table(
            'textitems', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False))
        self.textitems_l10n = sa.Table(
            'textitems_l10n', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('textitems'),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.UnicodeText))

    def create_models(self):
        class CommonBase(Base, Translatable):
            __translatable__ = {
                'locales': self.locales
            }
            locale = 'en'

        class TextItem(CommonBase):
            __translated_columns__ = [
                sa.Column('name', sa.UnicodeText),
            ]

        class TextItemL10N(BaseTranslationMixin):
            __parent_class__ = TextItem

        class Article(CommonBase, Translatable):
            __translated_columns__ = [
                sa.Column('content', sa.UnicodeText),
            ]

        class ArticleL10N(BaseTranslationMixin):
            __parent_class__ = Article

        self.TextItem = TextItem
        self.TextItemL10N = TextItemL10N
        self.Article = Article
        self.ArticleL10N = ArticleL10N

    def create_mappers(self):
        sa.orm.mapper(self.TextItem, self.textitems)
        sa.orm.mapper(self.TextItemL10N, self.textitems_l10n)
        TestCase.create_mappers(self)

    def test_translatable_dict_copied_to_each_child_class(self):
        assert self.Article.__translatable__['class'] == self.ArticleL10N
        assert self.TextItem.__translatable__['class'] == self.TextItemL10N
