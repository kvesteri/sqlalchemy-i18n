import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from tests import TestCase


class TestJoinExpressions(TestCase):
    def test_current_translation_as_expression(self):
        query = (
            self.session.query(self.Article)
            .join(self.Article.current_translation)
        )
        assert (
            'JOIN article_translation ON article.id = article_translation.id'
            ' AND article_translation.locale = :locale'
            in str(query)
        )

    def test_querying(self):
        query = (
            self.session.query(self.Article)
        )
        assert str(query) == (
            'SELECT article.id AS article_id, article.description AS'
            ' article_description \nFROM article'
        )
        query = (
            self.session.query(self.Article.__translatable__['class'])
        )
        assert 'article_translation.id AS article_translation_id' in str(query)
        assert (
            'article_translation.locale AS article_translation_locale'
            in str(query)
        )
        assert (
            'article_translation.name AS article_translation_name'
            in str(query)
        )
        assert (
            'article_translation.content AS article_translation_content'
            in str(query)
        )
        assert 'FROM article_translation' in str(query)


class TestJoinedLoading(TestCase):
    def setup_method(self, method):
        TestCase.setup_method(self, method)
        article = self.Article(
            description=u'Some desription',
            name=u'Some name'
        )
        self.session.add(article)
        self.session.commit()
        self.session.expunge_all()

    def test_joinedload_for_current_translation(self):
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.current_translation))
        ).first()
        query_count = self.connection.query_count
        article.name
        assert query_count == self.connection.query_count

    def test_contains_eager_for_current_translation(self):
        article = (
            self.session.query(self.Article)
            .join(self.Article.current_translation)
            .options(sa.orm.contains_eager(self.Article.current_translation))
        ).first()
        query_count = self.connection.query_count
        article.name
        assert query_count == self.connection.query_count

    def test_joinedload_for_single_translation(self):
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.translations['en']))
        ).first()
        query_count = self.connection.query_count
        article.name
        assert query_count == self.connection.query_count

    def test_joinedload_for_attr_accessor(self):
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.translations.en))
        ).first()
        query_count = self.connection.query_count
        article.name
        assert query_count == self.connection.query_count

    def test_joinedload_for_all_translations(self):
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.translations))
        ).first()
        query_count = self.connection.query_count
        article.name
        article.translations['fi'].name
        assert query_count == self.connection.query_count


class TestEditableDefaultLocale(TestCase):
    def setup_method(self, method):
        TestCase.setup_method(self, method)

        translation_cls = self.Article.__translatable__['class']
        self.Article.curr_translation = sa.orm.relationship(
            translation_cls,
            primaryjoin=sa.and_(
                self.Article.locale == translation_cls.locale,
                self.Article.id == translation_cls.id
            )
        )

        #self.Article.curr_translation = declared_attr(self.Article.curr_translation)

        article = self.Article(
            description=u'Some desription',
            name=u'Some name'
        )
        self.session.add(article)
        self.session.commit()

    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
                sa.Column('content', sa.UnicodeText)
            ]
            __translatable__ = {
                'base_classes': (self.Model, ),
                'locales': self.locales,
                'default_locale': 'en'
            }

            def get_locale(self):
                return self.locale or 'en'

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)
            locale = sa.Column(sa.Unicode(10))

        self.Article = Article

    def test_joinedload_for_current_translation2(self):
        print str(self.Article.curr_translation)
