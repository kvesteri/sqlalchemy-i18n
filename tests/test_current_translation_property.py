# -*- coding: utf-8 -*-

from tests import ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_as_object_property(self):
        article = self.Article()
        article.name = u'Some article'
        article.content = u'Some content'
        self.session.add(article)
        self.session.commit()
        assert article.current_translation.name == u'Some article'

    def test_as_class_property(self):
        assert self.Article.current_translation

    def test_setter(self):
        article = self.Article()
        article.current_translation = self.Article.__translatable__['class'](
            name=u'Something'
        )
        self.session.add(article)
        self.session.commit()
        assert article.name == u'Something'


class TestDeclarative(Suite, DeclarativeTestCase):
    pass


class TestClassic(Suite, ClassicTestCase):
    pass
