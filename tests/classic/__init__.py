import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_i18n import Translatable, translation_manager
from sqlalchemy_i18n.manager import BaseTranslationMixin
from tests import TestCase as DeclarativeTestCase


class Base(object):
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


class TestCase(DeclarativeTestCase):
    def setup_method(self, method):
        self.metadata = sa.MetaData()

        self.engine = sa.create_engine(
            'postgres://postgres@localhost/sqlalchemy_i18n_test'
        )
        #self.engine.echo = True
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
        self.articles = sa.Table(
            'articles', self.metadata,
            sa.Column('id', sa.Integer,
                      autoincrement=True,
                      primary_key=True,
                      nullable=False),
            sa.Column('description', sa.UnicodeText))
        self.articles_l10n = sa.Table(
            'articles_l10n', self.metadata,
            sa.Column('id', sa.Integer, sa.ForeignKey('articles',
                                                      ondelete="CASCADE"),
                      primary_key=True,
                      nullable=False),
            sa.Column('locale', sa.types.CHAR(2),
                      primary_key=True,
                      nullable=False),
            sa.Column('name', sa.Unicode(255)),
            sa.Column('content', sa.UnicodeText))

    def create_models(self):
        class Article(Base, Translatable):
            __translatable__ = {
                'locales': self.locales,
                'default_locale': 'en',
            }
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText),
            ]

            @hybrid_property
            def locale(self):
                return 'en'

        class ArticleL10N(Base, BaseTranslationMixin):
            __parent_class__ = Article

        self.Article = Article
        self.ArticleL10N = ArticleL10N

    def create_mappers(self):
        sa.orm.mapper(self.Article, self.articles)
        sa.orm.mapper(self.ArticleL10N, self.articles_l10n)
