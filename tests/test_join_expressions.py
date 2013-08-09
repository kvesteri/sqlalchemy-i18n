import sqlalchemy as sa
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

    def test_joinedload(self):
        article = (
            self.session.query(self.Article)
            .options(sa.orm.joinedload(self.Article.current_translation))
        ).first()
        query_count = self.connection.query_count
        article.name
        assert query_count == self.connection.query_count
