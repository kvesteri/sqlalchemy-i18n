# -*- coding: utf-8 -*-

import sqlalchemy as sa

from tests import ClassicTestCase, DeclarativeTestCase


class Suite(object):
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


class TestDeclarative(Suite, DeclarativeTestCase):
    def setup_method(self, method):
        DeclarativeTestCase.setup_method(self, method)
        article = self.Article(
            description=u'Some description',
            name=u'Some name'
        )
        self.session.add(article)
        self.session.commit()
        self.session.expunge_all()


class TestClassic(Suite, ClassicTestCase):
    def setup_method(self, method):
        ClassicTestCase.setup_method(self, method)
        article = self.Article(
            description=u'Some description',
            name=u'Some name'
        )
        self.session.add(article)
        self.session.commit()
        self.session.expunge_all()
