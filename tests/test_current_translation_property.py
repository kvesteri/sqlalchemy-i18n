# -*- coding: utf-8 -*-

from tests import DeclarativeTestCase, ClassicTestCase


class Suite(object):
    def test_as_object_property_with_force_locale(self):
        article = self.Article()
        article.name = u'Some article'
        article.content = u'Some content'
        self.session.add(article)
        self.session.commit()
        with article.force_locale('fi'):
            assert article.current_translation == article._translation_fi

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
