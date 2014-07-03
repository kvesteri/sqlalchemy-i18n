# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests.classic import Base, TestCase


class TestJoinedTableInheritance(TestCase):
    def create_tables(self):
        self.text_items = sa.Table(
            'text_items', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('description', sa.UnicodeText),
            sa.Column('discriminator', sa.Unicode(255)))
        self.text_items_l10n = sa.Table(
            'text_items_l10n', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('text_items.id',
                                                      ondelete="CASCADE"),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255), nullable=False),
            sa.Column('content', sa.UnicodeText, nullable=False),
            sa.Column('caption', sa.UnicodeText, nullable=False))
        self.articles = sa.Table(
            'articles', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('text_items.id',
                                                      ondelete="CASCADE"),
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('category', sa.Unicode(255)))

    def create_models(self):
        class TextItem(Base, Translatable):
            __translatable__ = {
                'locales': self.locales,
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
                sa.Column('content2', sa.UnicodeText),
            ]
            locale = 'en'

        class TextItemL10N(Base, BaseTranslationMixin):
            __parent_class__ = TextItem

        class Article(TextItem):
            pass

        self.TextItem = TextItem
        self.TextItemL10N = TextItemL10N
        self.Article = Article

    def create_mappers(self):
        sa.orm.mapper(self.TextItem, self.text_items,
                      polymorphic_on=self.text_items.c.discriminator)
        sa.orm.mapper(self.TextItemL10N, self.text_items_l10n)
        sa.orm.mapper(self.Article, self.articles,
                      inherits=self.TextItem,
                      polymorphic_identity=u'article')

    def test_auto_creates_relations(self):
        # textitem = self.TextItem()
        # assert textitem.translations
        # assert textitem._translations
        article = self.Article()
        assert article.translations

    def test_auto_creates_current_translation(self):
        # textitem = self.TextItem()
        # assert textitem.current_translation
        article = self.Article()
        assert article.current_translation

    def test_translatable_attributes(self):
        textitem = self.TextItem()
        class_ = textitem.__translatable__['class']
        assert class_.__name__ == 'TextItemL10N'

    def test_inherits_child_properties(self):
        assert self.Article.caption

    def test_table_name(self):
        article_l10n_mapper = sa.orm.class_mapper(self.Article.__translatable__['class'])
        table = article_l10n_mapper.local_table
        assert table.name == 'text_items_l10n'

    def test_translated_columns(self):
        article = self.Article()
        columns = sa.inspect(article.__translatable__['class']).columns
        assert 'caption' in columns
        assert 'name' in columns
        assert 'content' in columns
        assert 'description' not in columns

    def test_inherits_parent_table(self):
        article_l10n_mapper = sa.orm.class_mapper(self.Article.__translatable__['class'])
        textitem_l10n_mapper = sa.orm.class_mapper(self.TextItem.__translatable__['class'])
        article_l10n_table = article_l10n_mapper.local_table
        textitem_l10n_table = textitem_l10n_mapper.local_table
        assert article_l10n_table == textitem_l10n_table

    def test_property_delegators(self):
        article = self.Article()
        article.translations['en']

        assert not article.name
        article.current_translation.name = u'something'
        assert article.name == u'something'
        article.name = u'some other thing'
        assert article.current_translation.name == u'some other thing'
        assert article.translations['en'].name == u'some other thing'
        article.caption = u'some caption'
        assert article.current_translation.caption == u'some caption'
