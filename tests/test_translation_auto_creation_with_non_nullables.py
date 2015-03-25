# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy_i18n import Translatable, translation_base, translation_manager
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests import ClassicBase, ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_auto_sets_nullables_as_empty_strings(self):
        article = self.ExtendedArticle(
            name=u'Some article',
            content2=u'Some content'
        )
        self.session.add(article)
        self.session.commit()

        assert article.translations['en'].name == u'Some article'
        assert article.translations['fi'].name == u''


class TestDeclarative(Suite, DeclarativeTestCase):
    def setup_method(self, method):
        DeclarativeTestCase.setup_method(self, method)
        translation_manager.options['auto_created_locales'] = [u'fi', u'en']

    def teardown_method(self, method):
        DeclarativeTestCase.teardown_method(self, method)
        translation_manager.options['auto_created_locales'] = []

    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'auto_created_locales': True,
                'locales': ['en', 'fi']
            }

            @hybrid_property
            def locale(self):
                return 'en'

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)
            discriminator = sa.Column(sa.Unicode(255))

            __mapper_args__ = {
                'polymorphic_on': discriminator,
            }

        class ExtendedArticle(Article):
            __tablename__ = 'extended_article'
            __mapper_args__ = {'polymorphic_identity': u'extended'}
            id = sa.Column(
                sa.Integer, sa.ForeignKey(Article.id), primary_key=True
            )

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255), nullable=False)

            content = sa.Column(sa.UnicodeText)

            content2 = sa.Column(sa.UnicodeText)

        self.Article = Article
        self.ExtendedArticle = ExtendedArticle


class TestClassic(Suite, ClassicTestCase):
    def setup_method(self, method):
        ClassicTestCase.setup_method(self, method)
        translation_manager.options['auto_created_locales'] = [u'fi', u'en']

    def teardown_method(self, method):
        ClassicTestCase.teardown_method(self, method)
        translation_manager.options['auto_created_locales'] = []

    def create_tables(self):
        self.article = sa.Table(
            'article', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('description', sa.UnicodeText),
            sa.Column('discriminator', sa.Unicode(255)))
        self.extended_article = sa.Table(
            'extended_article', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('article.id'),
                      primary_key=True))
        self.article_translation = sa.Table(
            'article_translation', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('article.id',
                                                      ondelete="CASCADE"),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255), nullable=False),
            sa.Column('content', sa.UnicodeText, nullable=False),
            sa.Column('content2', sa.UnicodeText, nullable=False))

    def create_models(self):
        class Article(ClassicBase, Translatable):
            __translatable__ = {
                'locales': self.locales,
                'auto_created_locales': True,
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
                sa.Column('content2', sa.UnicodeText),
            ]

            @hybrid_property
            def locale(self):
                return 'en'

        class ExtendedArticle(Article):
            pass

        class ArticleTranslation(ClassicBase, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ExtendedArticle = ExtendedArticle
        self.ArticleTranslation = ArticleTranslation

    def create_mappers(self):
        sa.orm.mapper(self.Article, self.article,
                      polymorphic_on=self.article.c.discriminator)
        sa.orm.mapper(self.ExtendedArticle, self.extended_article,
                      inherits=self.Article,
                      polymorphic_identity=u'extended')
        sa.orm.mapper(self.ArticleTranslation, self.article_translation)
