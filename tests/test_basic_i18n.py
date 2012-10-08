from tests import TestCase


class TestTranslationModel(TestCase):
    def test_creates_translation_model_for_translatable_models(self):
        assert 'article' in self.Model.metadata.tables
        assert 'article_translation' in self.Model.metadata.tables

    def test_assigns_foreign_keys_from_parent(self):
        table = self.Model.metadata.tables['article_translation']
        assert len(table.foreign_keys) == 1

    def test_only_translated_columns_included_in_translation_table(self):
        table = self.Model.metadata.tables['article_translation']
        assert 'description' not in table.c

    def test_collection_maps_key_to_language(self):
        article = self.Article()
        translation = self.ArticleTranslation(
            name=u'Joku artikkeli', content=u'Jotain'
        )
        article.translations['fi'] = translation
        assert translation.language == u'fi'

    def test_column_proxies(self):
        article = self.Article()
        article.name = u'Some article'
        article.content = u'Some content'
        self.session.add(article)
        self.session.commit()
        assert article.translations['en'].name == u'Some article'
        assert article.translations['en'].content == u'Some content'
