# -*- coding: utf-8 -*-
import sqlalchemy as sa

from tests import ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_current_translation_as_expression(self):
        query = (
            self.session.query(self.Article)
            .join(self.Article.current_translation)
        )
        assert (
            'JOIN article_translation ON article.id = article_translation.id'
            ' AND article_translation.locale = '
            in str(query)
        )

    def test_order_by_translation(self):
        self.session.add(self.Article(name=u'cbc'))
        self.session.add(self.Article(name=u'abc'))
        self.session.add(self.Article(name=u'bbc'))
        self.session.commit()

        current_translation = sa.orm.aliased(self.Article.current_translation)
        articles = (
            self.session.query(self.Article)
            .join(current_translation, self.Article.current_translation)
            .options(sa.orm.contains_eager(
                self.Article.current_translation, alias=current_translation)
            )
            .order_by(current_translation.name)
        ).all()
        names = [a.name for a in articles]
        assert names == ['abc', 'bbc', 'cbc']

    def test_fallback_locale_as_expression(self):
        query = (
            self.session.query(self.Article)
            .join(self.Article.fallback_translation)
        )
        assert (
            'JOIN article_translation ON article.id = article_translation.id'
            ' AND article_translation.locale = '
            in str(query)
        )

    def test_querying(self):
        query = (
            self.session.query(self.Article)
        )
        assert str(query) == (
            'SELECT article.id AS article_id, article.description AS'
            ' article_description \nFROM article'
        )
        query = (
            self.session.query(self.Article.__translatable__['class'])
        )
        assert 'article_translation.id AS article_translation_id' in str(query)
        assert (
            'article_translation.locale AS article_translation_locale'
            in str(query)
        )
        assert (
            'article_translation.name AS article_translation_name'
            in str(query)
        )
        assert (
            'article_translation.content AS article_translation_content'
            in str(query)
        )
        assert 'FROM article_translation' in str(query)


class TestDeclarative(Suite, DeclarativeTestCase):
    pass


class TestClassic(Suite, ClassicTestCase):
    pass
