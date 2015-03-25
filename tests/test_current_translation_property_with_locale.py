# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy_i18n import Translatable, translation_base
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests import ClassicBase, ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_converts_locale_object_to_unicode(self):
        article = self.Article()
        article.name = u'Some article'
        assert article.name == u'Some article'


class Locale(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.value


class TestDeclarative(Suite, DeclarativeTestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'

            @hybrid_property
            def locale(self):
                return Locale('en')

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))
            content = sa.Column(sa.UnicodeText)

        self.Article = Article


class TestClassic(Suite, ClassicTestCase):
    def create_models(self):
        class Article(ClassicBase, Translatable):
            __translatable__ = {
                'locales': self.locales,
                'default_locale': 'en',
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

            @hybrid_property
            def locale(self):
                return Locale('en')

        class ArticleTranslation(ClassicBase, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation
