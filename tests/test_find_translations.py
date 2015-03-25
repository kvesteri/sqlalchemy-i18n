# -*- coding: utf-8 -*-

from decimal import Decimal

from sqlalchemy_i18n import find_translations
from tests import ClassicTestCase, DeclarativeTestCase


class Suite(object):
    locales = ['en', 'fi', 'sv']

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
            u'Joku artikkeli': Decimal('1.0')
        }

    def test_with_varying_confidence(self):
        article = self.Article()
        article.translations['en'].name = u'Some article'
        article.translations['en'].content = u'Some content'
        article.translations['fi'].name = u'Joku artikkeli'
        article.translations['fi'].content = u'Jotain tekstii'
        self.session.add(article)
        article = self.Article()
        article.translations['en'].name = u'Some article'
        article.translations['en'].content = u'Some content'
        article.translations['fi'].name = u'Joku toinen artikkeli'
        article.translations['fi'].content = u'Jotain muuta tekstii'
        self.session.add(article)

        self.session.commit()

        article = self.Article()
        article.translations['en'].name = u'Some article'
        self.session.add(article)
        self.session.commit()

        assert dict(find_translations(article, 'name', 'fi').all()) == {
            u'Joku artikkeli': Decimal('0.5'),
            u'Joku toinen artikkeli': Decimal('0.5')
        }


class TestDeclarative(Suite, DeclarativeTestCase):
    pass


class TestClassic(Suite, ClassicTestCase):
    pass
