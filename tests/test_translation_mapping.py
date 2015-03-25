# -*- coding: utf-8 -*-

from pytest import raises

from sqlalchemy_i18n import UnknownLocaleError
from tests import ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_proxy_contains(self):
        article = self.Article()
        article.translations['en']
        assert 'en' in article.translations

    def test_translation_mapping_attribute_getter(self):
        article = self.Article()
        article.translations.en.name = 'Something'
        assert article.name == 'Something'

    def test_attribute_accessor_for_unknown_locale(self):
        with raises(UnknownLocaleError):
            self.Article.translations.some_unknown_locale

    def test_proxy_not_contains(self):
        article = self.Article()
        assert 'unknown_locale' not in article.translations

    def test_items(self):
        article = self.create_article()
        assert isinstance(article.translations.items(), list)

    def test_iteritems(self):
        article = self.create_article()
        assert (
            article.translations.items() ==
            list(article.translations.iteritems())
        )

    def test_set_item(self):
        article = self.create_article()
        self.session.expunge_all()
        article = self.session.query(self.Article).first()
        locale_obj = self.Article.__translatable__['class'](
            name=u'Some other thing'
        )
        article.translations['en'] = locale_obj
        self.session.commit()
        self.session.expunge_all()
        article = self.session.query(self.Article).first()

        assert article.translations['en'].name == u'Some other thing'

    def test_repr(self):
        article = self.create_article()
        assert (
            repr(article.translations) ==
            'TranslationsMapping(Article(id=%d))' % article.id
        )

    def test_iter(self):
        article = self.create_article()
        assert len(list(article.translations)) == 2

    def test_values(self):
        article = self.create_article()
        values = list(article.translations.values())
        for value in values:
            assert isinstance(value, article.__translatable__['class'])
        assert len(values) == 2


class TestDeclarative(Suite, DeclarativeTestCase):
    pass


class TestClassic(Suite, ClassicTestCase):
    pass
