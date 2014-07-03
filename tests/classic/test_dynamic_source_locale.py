# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_i18n import Translatable, UnknownLocaleError
from sqlalchemy_i18n.manager import BaseTranslationMixin
from pytest import raises
from tests.classic import Base, TestCase


class TestHybridPropertyAsDynamicSourceLocale(TestCase):
    def setup_method(self, method):
        TestCase.setup_method(self, method)

        article = self.Article(description=u'Some description',
                               name=u'Some name')
        self.session.add(article)
        self.session.commit()

    def create_tables(self):
        self.articles = sa.Table(
            'articles', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('description', sa.UnicodeText),
            sa.Column('_locale', sa.types.CHAR(2), default=u'en'))
        self.articles_l10n = sa.Table(
            'articles_l10n', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('articles'),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255)),
            sa.Column('content', sa.UnicodeText))

    def create_models(self):
        class Article(Base, Translatable):
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

        class ArticleL10N(Base, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleL10N = ArticleL10N

    def test_joinedload_for_current_translation(self):
        count = self.connection.query_count
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.current_translation))
        ).first()
        article.translations['en']

        assert self.connection.query_count == count + 1


class TestColumnAsDynamicSourceLocale(TestCase):
    def create_tables(self):
        self.articles = sa.Table(
            'articles', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('description', sa.UnicodeText),
            sa.Column('locale', sa.types.CHAR(2), default=u'en'))
        self.articles_l10n = sa.Table(
            'articles_l10n', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('articles'),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255)),
            sa.Column('content', sa.UnicodeText))

    def create_models(self):
        class Article(Base, Translatable):
            __translatable__ = {
                'locales': self.locales
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

        class ArticleL10N(Base, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleL10N = ArticleL10N

    def test_current_translation_when_locale_not_set(self):
        with raises(UnknownLocaleError):
            self.Article(name='some article')
