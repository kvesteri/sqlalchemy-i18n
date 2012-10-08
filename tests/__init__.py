import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_i18n import Translatable, translated_session


class TestCase(object):
    def setup_method(self, method):
        self.engine = create_engine('sqlite:///:memory:')
        #self.engine.echo = True
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
