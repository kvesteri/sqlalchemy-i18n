# -*- coding: utf-8 -*-

from sqlalchemy_i18n import translation_manager
from tests import ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_auto_creates_translation_objects(self):
        article = self.Article(name=u'Some article')
        self.session.add(article)
        self.session.commit()

        assert 'en' in article.translations
        assert article.translations['en']
        assert 'fi' in article.translations
        assert article.translations['fi']


class TestDeclarative(Suite, DeclarativeTestCase):
    def setup_method(self, method):
        DeclarativeTestCase.setup_method(self, method)
        translation_manager.options['auto_created_locales'] = [u'fi', u'en']

    def teardown_method(self, method):
        DeclarativeTestCase.teardown_method(self, method)
        translation_manager.options['auto_created_locales'] = []


class TestClassic(Suite, ClassicTestCase):
    def setup_method(self, method):
        ClassicTestCase.setup_method(self, method)
        translation_manager.options['auto_created_locales'] = [u'fi', u'en']

    def teardown_method(self, method):
        ClassicTestCase.teardown_method(self, method)
        translation_manager.options['auto_created_locales'] = []
