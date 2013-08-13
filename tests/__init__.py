import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_i18n import Translatable, make_translatable


@sa.event.listens_for(Engine, 'before_cursor_execute')
def count_sql_calls(conn, cursor, statement, parameters, context, executemany):
    conn.query_count += 1


make_translatable(options={'locales': ['en', 'fi']})


class TestCase(object):
    def setup_method(self, method):
        self.engine = create_engine(
            'postgres://postgres@localhost/sqlalchemy_i18n_test'
        )
        #self.engine.echo = True
        self.connection = self.engine.connect()
        self.connection.query_count = 0
        self.Model = declarative_base()

        self.create_models()

        sa.orm.configure_mappers()
        self.Model.metadata.create_all(self.connection)

        Session = sessionmaker(bind=self.connection)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.Model.metadata.drop_all(self.connection)
        self.connection.close()
        self.engine.dispose()

    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText)
            ]
            __translatable__ = {
                'base_classes': (self.Model, ),
                'locales': ['en', 'fi'],
                'default_locale': 'en'
            }

            def get_locale(self):
                return 'en'

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)

        self.Article = Article
