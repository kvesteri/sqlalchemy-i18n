# -*- coding: utf-8 -*-

import sqlalchemy as sa

from sqlalchemy_i18n import Translatable, translation_base
from tests import DeclarativeTestCase


class Suite(object):
    def test_translatable_dict_copied_to_each_child_class(self):
        assert issubclass(self.ArticleTranslation, self.TranslationBase)


class TestDeclarative(Suite, DeclarativeTestCase):
    def create_models(self):
        class Base(self.Model):
            __abstract__ = True
            __versioned__ = {}

        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            id = sa.Column(
                sa.Integer, primary_key=True
            )

        class ArticleTranslation(
            translation_base(Article, base_class_factory=lambda cls: Base)
        ):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

        self.TranslationBase = Base
        self.Article = Article
        self.ArticleTranslation = ArticleTranslation


# This is the common case in Classic mapping, no test needed
