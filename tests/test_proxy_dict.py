from flexmock import flexmock
from sqlalchemy_i18n import ProxyDict
from tests import TestCase


class TestProxyDict(TestCase):
    def test_access_key_for_pending_parent(self):
        article = self.Article()
        self.session.add(article)
        assert article.translations['en']

    def test_access_key_for_transient_parent(self):
        article = self.Article()
        assert article.translations['en']

    def test_cache(self):
        article = self.Article()
        (
            flexmock(ProxyDict)
            .should_receive('fetch')
            .once()
        )
        self.session.add(article)
        self.session.commit()
        article.translations['en']
        article.translations['en']

    def test_set_updates_cache(self):
        article = self.Article()
        (
            flexmock(ProxyDict)
            .should_receive('fetch')
            .once()
        )
        self.session.add(article)
        self.session.commit()
        article.translations['en']
        article.translations['en'] = self.Article.__translatable__['class'](
            locale='en',
            name=u'something'
        )
        article.translations['en']
