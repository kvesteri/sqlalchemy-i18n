# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy_i18n import Translatable, translation_base
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests import ClassicBase, ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_joinedload_for_current_translation(self):
        count = self.connection.query_count
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.current_translation))
        ).first()
        article.translations['en']

        assert self.connection.query_count == count + 1


class TestDeclarative(Suite, DeclarativeTestCase):
    def setup_method(self, method):
        DeclarativeTestCase.setup_method(self, method)
        self.ArticleTranslation = self.Article.__translatable__['class']

        article = self.Article(
            description=u'Some description',
            name=u'Some name'
        )
        self.session.add(article)
        self.session.commit()

    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': self.locales
            }

            @hybrid_property
            def locale(self):
                return self._locale or 'en'

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)
            _locale = sa.Column(sa.Unicode(10), default=u'en')

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))
            content = sa.Column(sa.UnicodeText)

        self.Article = Article


class TestClassic(Suite, ClassicTestCase):
    def setup_method(self, method):
        ClassicTestCase.setup_method(self, method)

        article = self.Article(description=u'Some description',
                               name=u'Some name')
        self.session.add(article)
        self.session.commit()

    def create_tables(self):
        self.article = sa.Table(
            'article', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('description', sa.UnicodeText),
            sa.Column('_locale', sa.types.CHAR(2), default=u'en'))
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

            @hybrid_property
            def locale(self):
                return self._locale or 'en'

        class ArticleTranslation(ClassicBase, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation
