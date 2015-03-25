# -*- coding: utf-8 -*-

from pytest import raises

from sqlalchemy_i18n import UnknownLocaleError
from tests import ClassicTestCase, DeclarativeTestCase


class Suite(object):
    def test_attribute_accessor_for_unknown_locale(self):
        with raises(UnknownLocaleError):
            assert self.Article.translations.some_unknown_locale

    def test_attribute_accessors(self):
        assert self.Article.translations.en
        assert self.Article.translations.fi


class TestDeclarative(Suite, DeclarativeTestCase):
    pass


class TestClassic(Suite, ClassicTestCase):
    pass
