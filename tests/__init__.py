import warnings

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker
from sqlalchemy_i18n import (
    Translatable, translation_manager, make_translatable, translation_base
)


@sa.event.listens_for(Engine, 'before_cursor_execute')
def count_sql_calls(conn, cursor, statement, parameters, context, executemany):
    conn.query_count += 1


make_translatable(options={'locales': ['en', 'fi']})


warnings.simplefilter('error', sa.exc.SAWarning)


class TestCase(object):
    locales = ['en', 'fi']
    create_tables = True
    configure_mappers = True

    def create_session(self):
        Session = sessionmaker(bind=self.connection)
        self.session = Session()

    def setup_method(self, method):
        self.engine = create_engine(
            'postgres://postgres@localhost/sqlalchemy_i18n_test'
        )
        # self.engine.echo = True
        self.connection = self.engine.connect()
        self.connection.query_count = 0
        self.Model = declarative_base()

        self.create_models()

        if self.configure_mappers:
            sa.orm.configure_mappers()
        if self.create_tables:
            self.Model.metadata.create_all(self.connection)
        self.create_session()

    def teardown_method(self, method):
        translation_manager.pending_classes = []
        self.session.close_all()
        self.Model.metadata.drop_all(self.connection)
        self.connection.close()
        self.engine.dispose()

    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': self.locales,
                'default_locale': 'en'
            }

            @hybrid_property
            def locale(self):
                return 'en'

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)

            def __repr__(self):
                return 'Article(id=%r)' % self.id

        class ArticleTranslation(translation_base(Article)):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

            content = sa.Column(sa.UnicodeText)

        self.Article = Article

    def create_article(self):
        article = self.Article(name=u'Something', content=u'Something')
        self.session.add(article)
        self.session.commit()
        return article
