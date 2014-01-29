from pytest import raises
from sqlalchemy_i18n import UnknownLocaleError
from tests import TestCase


class TestTranslationMapping(TestCase):
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
        assert 'dsadsad' not in article.translations
