# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_i18n import Translatable, translation_manager
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests.classic import Base, TestCase


class TestTranslationAutoCreation(TestCase):
    def setup_method(self, method):
        TestCase.setup_method(self, method)
        translation_manager.options['auto_created_locales'] = [u'fi', u'en']

    def teardown_method(self, method):
        TestCase.teardown_method(self, method)
        translation_manager.options['auto_created_locales'] = []

    def test_auto_creates_translation_objects(self):
        article = self.Article(name=u'Some article')
        self.session.add(article)
        self.session.commit()

        assert 'en' in article.translations
        assert article.translations['en']
        assert 'fi' in article.translations
        assert article.translations['fi']


class TestTranslationAutoCreationWithNonNullables(TestCase):
    def setup_method(self, method):
        TestCase.setup_method(self, method)
        translation_manager.options['auto_created_locales'] = [u'fi', u'en']

    def teardown_method(self, method):
        TestCase.teardown_method(self, method)
        translation_manager.options['auto_created_locales'] = []

    def create_tables(self):
        self.articles = sa.Table(
            'articles', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('description', sa.UnicodeText),
            sa.Column('discriminator', sa.Unicode(255)))
        self.extended_articles = sa.Table(
            'extended_articles', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('articles.id'),
                      primary_key=True))
        self.articles_l10n = sa.Table(
            'articles_l10n', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('articles.id',
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
        class Article(Base, Translatable):
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

        class ArticleL10N(Base, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ExtendedArticle = ExtendedArticle
        self.ArticleL10N = ArticleL10N

    def create_mappers(self):
        sa.orm.mapper(self.Article, self.articles,
                      polymorphic_on=self.articles.c.discriminator)
        sa.orm.mapper(self.ExtendedArticle, self.extended_articles,
                      inherits=self.Article,
                      polymorphic_identity=u'extended')
        sa.orm.mapper(self.ArticleL10N, self.articles_l10n)

    def test_auto_sets_nullables_as_empty_strings(self):
        article = self.ExtendedArticle(
            name=u'Some article',
            content2=u'Some content'
        )
        self.session.add(article)
        self.session.commit()

        assert article.translations['en'].name == u'Some article'
        assert article.translations['fi'].name == u''
