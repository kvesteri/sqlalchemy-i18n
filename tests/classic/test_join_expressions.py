# -*- coding: utf-8 -*-
import sqlalchemy as sa
from tests.classic import TestCase


class TestJoinExpressions(TestCase):
    def test_current_translation_as_expression(self):
        query = (
            self.session.query(self.Article)
            .join(self.Article.current_translation)
        )
        assert (
            'JOIN articles_l10n ON articles.id = articles_l10n.id'
            ' AND articles_l10n.locale = :locale'
            in str(query)
        )

    def test_querying(self):
        query = (
            self.session.query(self.Article)
        )
        assert str(query) == (
            'SELECT articles.id AS articles_id, articles.description AS'
            ' articles_description \nFROM articles'
        )
        query = (
            self.session.query(self.Article.__translatable__['class'])
        )
        assert 'articles_l10n.id AS articles_l10n_id' in str(query)
        assert (
            'articles_l10n.locale AS articles_l10n_locale'
            in str(query)
        )
        assert (
            'articles_l10n.name AS articles_l10n_name'
            in str(query)
        )
        assert (
            'articles_l10n.content AS articles_l10n_content'
            in str(query)
        )
        assert 'FROM articles_l10n' in str(query)


class TestJoinedLoading(TestCase):
    def setup_method(self, method):
        TestCase.setup_method(self, method)
        article = self.Article(
            description=u'Some description',
            name=u'Some name'
        )
        self.session.add(article)
        self.session.commit()
        self.session.expunge_all()

    def test_joinedload_for_current_translation(self):
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.current_translation))
        ).first()
        query_count = self.connection.query_count
        article.name
        assert query_count == self.connection.query_count

    def test_contains_eager_for_current_translation(self):
        article = (
            self.session.query(self.Article)
            .join(self.Article.current_translation)
            .options(sa.orm.contains_eager(self.Article.current_translation))
        ).first()
        query_count = self.connection.query_count
        article.name
        assert query_count == self.connection.query_count

    def test_joinedload_for_single_translation(self):
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.translations['en']))
        ).first()
        query_count = self.connection.query_count
        article.name
        assert query_count == self.connection.query_count

    def test_joinedload_for_attr_accessor(self):
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.translations.en))
        ).first()
        query_count = self.connection.query_count
        article.name
        assert query_count == self.connection.query_count

    def test_joinedload_for_all_translations(self):
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.translations))
        ).first()
        query_count = self.connection.query_count
        article.name
        article.translations['fi'].name
        assert query_count == self.connection.query_count
