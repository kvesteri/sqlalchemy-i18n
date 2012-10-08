from sqlalchemy.schema import UniqueConstraint
from tests import TestCase


class TestTranslatableModel(TestCase):
    def test_creates_translation_model_for_translatable_models(self):
        assert 'article' in self.Model.metadata.tables

    def test_appends_language_column_to_article_table(self):
        table = self.Model.metadata.tables['article']
        assert 'language' in table.c

    def test_appends_language_column_to_article_model(self):
        article = self.Article()
        article.language = u'en'
        article.content = u'some content'
        article.name = u'some name'
        self.session.add(article)
        self.session.commit()
        self.session.expunge_all()

        article = self.session.query(self.Article).get((u'en', 1))
        assert article.language == u'en'

    def test_appends_unique_constraint_to_language_and_pks(self):
        constraint_classes = [
            c.__class__ for c in self.Article.__table__.constraints
        ]
        assert UniqueConstraint in constraint_classes

    def test_mass_update(self):
        article_en = self.Article()
        article_en.language = u'en'
        article_en.content = u'some content'
        article_en.name = u'some name'
        self.session.add(article_en)
        self.session.commit()
        article_fi = self.Article()
        article_fi.id = article_en.id
        article_fi.language = u'fi'
        article_fi.content = u'jotain kontenttia'
        article_fi.name = u'joku nimi'
        self.session.add(article_fi)
        self.session.commit()
        article_en.mass_update('description', u'some description')
        self.session.commit()

        for article in self.session.query(self.Article).all():
            assert article.description == u'some description'
