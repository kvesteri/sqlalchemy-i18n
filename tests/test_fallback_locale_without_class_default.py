# -*- coding: utf-8 -*-

import sqlalchemy as sa

from sqlalchemy_i18n import Translatable, translation_base
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests import ClassicBase
from tests.test_fallback_locale_as_callable import TestClassic as TCBase
from tests.test_fallback_locale_as_callable import TestDeclarative as TDBase


class TestDeclarative(TDBase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': self.locales,
                'auto_create_locales': True,
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            locale = sa.Column(sa.Unicode(255), default=u'en')

            def get_locale(self):
                return 'en'

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

        self.Article = Article


class TestClassic(TCBase):
    def create_models(self):
        class Article(ClassicBase, Translatable):
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

        class ArticleTranslation(ClassicBase, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation
