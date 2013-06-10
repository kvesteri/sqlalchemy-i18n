from tests import TestCase


class TestTranslatableModel(TestCase):
    def test_auto_creates_relations(self):
        article = self.Article()
        assert article.translations
        assert article._translations

    def test_auto_creates_current_translation(self):
        article = self.Article()
        assert article.current_translation

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

    def test_proxy_contains(self):
        article = self.Article()
        article.translations['en']
        assert 'en' in article.translations

    def test_proxy_not_contains(self):
        article = self.Article()
        assert 'en' not in article.translations

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

    def test_current_translation_as_expression(self):
        query = (
            self.session.query(self.Article)
            .join(self.Article.current_translation)
        )
        assert (
            'JOIN article_translation ON article.id = article_translation.id'
            ' AND article_translation.locale = :locale'
            in str(query)
        )

    def test_translations_as_expression(self):
        query = (
            self.session.query(self.Article)
            .join(self.Article.translations)
        )
        assert (
            'SELECT article.id AS article_id, article.description AS '
            'article_description \nFROM article JOIN article_translation '
            'ON article.id = article_translation.id'
        ) == str(query)

    def test_querying(self):
        query = (
            self.session.query(self.Article)
        )
        assert str(query) == (
            'SELECT article.id AS article_id, article.description AS'
            ' article_description \nFROM article'
        )
        query = (
            self.session.query(self.Article.__translatable__['class'])
        )
        assert str(query) == (
            'SELECT article_translation.id AS article_translation_id, '
            'article_translation.locale AS article_translation_locale, '
            'article_translation.name AS article_translation_name, '
            'article_translation.content AS article_translation_content '
            '\nFROM article_translation'
        )

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

    def test_hybrid_properties_default_locale(self):
        article = self.Article()
        article.name = u'Some article'
        article.content = u'Some content'
        self.session.add(article)
        self.session.commit()
        with article.force_locale('fi'):
            article.content = u'Jotain tekstii'
            assert article.name == u'Some article'
            assert article.content == u'Jotain tekstii'
        assert article.name == u'Some article'
        assert article.content == u'Some content'

    def test_force_locale(self):
        article = self.Article()
        article._get_locale() == 'en'
        with article.force_locale('fi'):
            assert article._get_locale() == 'fi'
        assert article._get_locale() == 'en'

    def test_nested_force_locale(self):
        article = self.Article()
        article._get_locale() == 'en'
        with article.force_locale('fi'):
            with article.force_locale('sv'):
                assert article._get_locale() == 'sv'
            assert article._get_locale() == 'fi'
        assert article._get_locale() == 'en'

    def test_current_translation_as_object_property(self):
        article = self.Article()
        article.name = u'Some article'
        article.content = u'Some content'
        self.session.add(article)
        self.session.commit()
        with article.force_locale('fi'):
            print self.connection.query_count
            assert article.current_translation == article._translation_fi

            assert article.current_translation == article._translation_fi
            print self.connection.query_count
            article._translation_fi
            print self.connection.query_count
