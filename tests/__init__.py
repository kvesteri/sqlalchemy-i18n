# -*- coding: utf-8 -*-

import warnings

import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker

from sqlalchemy_i18n import (
    make_translatable,
    Translatable,
    translation_base,
    translation_manager
)
from sqlalchemy_i18n.manager import BaseTranslationMixin


@sa.event.listens_for(Engine, 'before_cursor_execute')
def count_sql_calls(conn, cursor, statement, parameters, context, executemany):
    conn.query_count += 1


make_translatable(options={'locales': ['en', 'fi']})


warnings.simplefilter('error', sa.exc.SAWarning)


sqlalchemy_utils.i18n.get_locale = lambda: 'en'


class DeclarativeTestCase(object):
    engine_uri = 'postgres://postgres@localhost/sqlalchemy_i18n_test'
    locales = ['en', 'fi']
    create_tables = True
    configure_mappers = True

    def create_session(self):
        Session = sessionmaker(bind=self.connection)
        self.session = Session()

    def setup_method(self, method):
        self.engine = create_engine(self.engine_uri)
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
        self.ArticleTranslation = ArticleTranslation

    def create_article(self):
        article = self.Article(name=u'Something', content=u'Something')
        self.session.add(article)
        self.session.commit()
        return article


class ClassicBase(object):
    def __init__(self, **kwargs):
        cls_ = type(self)
        for k in kwargs:
            if not hasattr(cls_, k):
                raise TypeError(
                    "%r is an invalid keyword argument for %s" %
                    (k, cls_.__name__))
            setattr(self, k, kwargs[k])

    def __repr__(self):
        "Return an ASCII representation of the entity."

        from sqlalchemy.orm.exc import DetachedInstanceError

        mapper = sa.orm.object_mapper(self)
        pkeyf = mapper.primary_key
        try:
            pkeyv = mapper.primary_key_from_instance(self)
        except DetachedInstanceError:
            keys = "detached-instance"
        else:
            keys = ', '.join(u'%s=%r' % (f.name, v)
                             for f, v in zip(pkeyf, pkeyv))
        return '%s(%s)' % (self.__class__.__name__, keys)


class ClassicTestCase(DeclarativeTestCase):
    def setup_method(self, method):
        self.metadata = sa.MetaData()

        self.engine = sa.create_engine(self.engine_uri)
        # self.engine.echo = True
        self.connection = self.engine.connect()
        self.connection.query_count = 0

        self.create_tables()
        self.create_models()
        self.create_mappers()

        if self.configure_mappers:
            sa.orm.configure_mappers()

        if self.create_tables:
            self.metadata.create_all(self.connection)

        self.create_session()

    def teardown_method(self, method):
        translation_manager.pending_classes = []
        self.session.close_all()
        self.metadata.drop_all(self.connection)
        self.connection.close()
        self.engine.dispose()

    def create_tables(self):
        self.article = sa.Table(
            'article', self.metadata,
            sa.Column(
                'id',
                sa.Integer,
                autoincrement=True,
                primary_key=True,
                nullable=False
            ),
            sa.Column('description', sa.UnicodeText)
        )
        self.article_translation = sa.Table(
            'article_translation',
            self.metadata,
            sa.Column(
                'id',
                sa.Integer,
                sa.ForeignKey(
                    'article',
                    ondelete="CASCADE"
                ),
                primary_key=True,
                nullable=False
            ),
            sa.Column(
                'locale',
                sa.types.CHAR(2),
                primary_key=True,
                nullable=False
            ),
            sa.Column('name', sa.Unicode(255)),
            sa.Column('content', sa.UnicodeText)
        )

    def create_models(self):
        class Article(ClassicBase, Translatable):
            __translatable__ = {
                'locales': self.locales,
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

            @hybrid_property
            def locale(self):
                return 'en'

        class ArticleTranslation(ClassicBase, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation

    def create_mappers(self):
        sa.orm.mapper(self.Article, self.article)
        sa.orm.mapper(self.ArticleTranslation, self.article_translation)
