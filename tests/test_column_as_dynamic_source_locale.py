# -*- coding: utf-8 -*-

from pytest import raises
import sqlalchemy as sa
from sqlalchemy_i18n import Translatable, translation_base, UnknownLocaleError
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests import DeclarativeTestCase, ClassicTestCase, ClassicBase


class Suite(object):
    def test_current_translation_when_locale_not_set(self):
        with raises(UnknownLocaleError):
            self.Article(name='some article')


class TestDeclarative(Suite, DeclarativeTestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': self.locales
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)
            locale = sa.Column(sa.Unicode(10), default=u'en')

            def __repr__(self):
                return 'Article(%r)' % self.name

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))
            content = sa.Column(sa.UnicodeText)

        self.Article = Article


class TestClassic(Suite, ClassicTestCase):
    def create_tables(self):
        self.article = sa.Table(
            'article', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('description', sa.UnicodeText),
            sa.Column('locale', sa.types.CHAR(2), default=u'en'))
        self.article_translation = sa.Table(
            'article_translation', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('article'),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255)),
            sa.Column('content', sa.UnicodeText))

    def create_models(self):
        class Article(ClassicBase, Translatable):
            __translatable__ = {
                'locales': self.locales
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

        class ArticleTranslation(ClassicBase, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation
