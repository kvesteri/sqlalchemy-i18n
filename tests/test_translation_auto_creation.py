from sqlalchemy_i18n import translation_manager
from tests import TestCase


class TestTranslationAutoCreation(TestCase):
    def setup_method(self, method):
        TestCase.setup_method(self, method)
        translation_manager.options['auto_created_locales'] = [u'fi', u'en']

    def teardown_method(self, method):
        TestCase.teardown_method(self, method)
        translation_manager.options['auto_created_locales'] = []

    def test_auto_creates_translation_objects(self):
        article = self.Article(name=u'Some article')
        self.session.add(article)
        self.session.commit()

        assert 'en' in article.translations
        assert article.translations['en']
        assert 'fi' in article.translations
        assert article.translations['fi']
