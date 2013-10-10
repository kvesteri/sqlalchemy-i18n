from decimal import Decimal
from sqlalchemy_i18n import find_translations
from tests import TestCase


class TestFindTranslations(TestCase):
    def test_with_full_confidence(self):
        article = self.Article()
        article.translations['en'].name = u'Some article'
        article.translations['en'].content = u'Some content'
        article.translations['fi'].name = u'Joku artikkeli'
        article.translations['fi'].content = u'Jotain tekstii'
        self.session.add(article)
        self.session.commit()

        article = self.Article()
        article.translations['en'].name = u'Some article'
        self.session.add(article)
        self.session.commit()
        assert dict(find_translations(article, 'name', 'fi')) == {
            u'Joku artikkeli': Decimal(1.0)
        }
