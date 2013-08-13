import sqlalchemy as sa
from sqlalchemy_i18n import Translatable
from tests import TestCase


class TestRelationships(TestCase):
    def create_models(self):
        class Article(self.Model):
            __tablename__ = 'article'
            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            content = sa.Column(sa.UnicodeText)

        class Category(self.Model, Translatable):
            __tablename__ = 'category'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255)),
            ]
            __translatable__ = {
                'base_classes': (self.Model, )
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            article_id = sa.Column(sa.Integer, sa.ForeignKey(Article.id))
            article = sa.orm.relationship(
                Article,
                backref=sa.orm.backref(
                    'categories',
                    passive_deletes=True,
                    cascade='all, delete-orphan'
                )
            )

        self.Article = Article
        self.Category = Category

    def test_nullify_relation(self):
        self.CategoryTranslation = self.Category.__translatable__['class']
        article = self.Article()
        article.content = u'Some content'
        article.categories.append(self.Category())
        self.session.commit()
        article.categories = []
        self.session.commit()
        assert not self.session.query(self.CategoryTranslation).count()
