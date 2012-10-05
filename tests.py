import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_i18n import Translatable, translated_session


class TestCase(object):
    def setup_method(self, method):
        self.engine = create_engine('sqlite:///:memory:')
        self.Model = declarative_base()

        self.Article = self.create_models()
        self.ArticleTranslation = self.Article.__translation_mapper__.class_
        self.Model.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = translated_session(Session())

    def teardown_method(self, method):
        self.session.close_all()
        self.Model.metadata.drop_all(self.engine)
        self.engine.dispose()

    def create_models(self):
        class Article(Translatable, self.Model):
            __tablename__ = 'article'
            __translated_columns__ = ['name', 'content']

            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.Unicode(255))
            content = sa.Column(sa.UnicodeText)
            description = sa.Column(sa.UnicodeText)
        return Article


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
