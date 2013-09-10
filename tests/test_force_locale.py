from tests import TestCase


class TestTranslatableModel(TestCase):
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

    def test_fallback_locale(self):
        article = self.Article()
        article.name = u'Some article'
        article.content = u'Some content'
        with article.force_locale('fi'):
            article.name = u''
            assert article.name == u'Some article'
