from tests import TestCase


class TestTranslatableModel(TestCase):
    def test_auto_creates_relations(self):
        article = self.Article()
        assert article.translations

    def test_translatable_attributes(self):
        article = self.Article()
        assert article.__translatable__['class']
        assert article.__translatable__['class'].__name__ == (
            'ArticleTranslation'
        )

    def test_relationship_consistency(self):
        article = self.Article()
        article.name = u'Some article'
        assert article.current_translation == article.translations['en']

    def test_translated_columns(self):
        article = self.Article()
        columns = article.__translatable__['class'].__table__.c
        assert 'name' in columns
        assert 'content' in columns
        assert 'description' not in columns

    def test_property_delegators(self):
        article = self.Article()
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

    def test_commit_session(self):
        article = self.Article()
        article.name = u'Some article'
        article.content = u'Some content'
        self.session.add(article)
        self.session.commit()
        article = self.session.query(self.Article).get(1)
        assert article.name == u'Some article'
        assert article.content == u'Some content'

    def test_delete(self):
        article = self.Article()
        article.description = u'Some description'
        self.session.add(article)
        self.session.commit()
        article.name = u'Some article'
        article.content = u'Some content'
        self.session.delete(article)
        self.session.commit()
