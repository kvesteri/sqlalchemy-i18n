from flexmock import flexmock
from sqlalchemy_i18n import ProxyDict
from tests import TestCase


class TestTranslatableModel(TestCase):
    def test_auto_creates_relation(self):
        article = self.Article()
        assert article.translations
        assert article._translations

    def test_auto_creates_current_translation(self):
        article = self.Article()
        assert article.current_translation

    def test_translatable_attributes(self):
        article = self.Article()
        assert article.__translatable__['class']

    def test_translated_columns(self):
        article = self.Article()
        columns = article.__translatable__['class'].__table__.c
        assert 'name' in columns
        assert 'content' in columns
        assert 'description' not in columns

    def test_property_delegators(self):
        article = self.Article()
        article._translations.count()
        article.translations['en']

        assert not article.name
        article.current_translation.name = u'something'
        assert article.name == u'something'
        article.name = u'some other thing'
        assert article.current_translation.name == u'some other thing'
        assert article.translations['en'].name == u'some other thing'

    def test_appends_locale_column_to_translation_table(self):
        table = self.Model.metadata.tables['article_translation']
        assert 'locale' in table.c

    def test_hybrid_properties(self):
        query = (
            self.session.query(self.Article)
            .join(self.Article.current_translation)
        )
        assert (
            'JOIN article_translation ON article.id = article_translation.id'
            ' AND article_translation.locale = :locale'
            in str(query)
        )


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
