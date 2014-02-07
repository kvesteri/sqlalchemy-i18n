import sqlalchemy as sa
from sqlalchemy_i18n import Translatable, translation_base
from tests import TestCase


class TestJoinedTableInheritance(TestCase):
    def create_models(self):
        class TextItem(self.Model, Translatable):
            __tablename__ = 'text_item'
            __translatable__ = {
                'locales': ['en', 'fi'],
            }
            locale = 'en'

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            description = sa.Column(sa.UnicodeText)
            discriminator = sa.Column(
                sa.Unicode(100)
            )
            __mapper_args__ = {
                'polymorphic_on': discriminator,
            }

        class TextItemTranslation(translation_base(TextItem)):
            __tablename__ = 'text_item_translation'
            name = sa.Column(sa.Unicode(255))

            content = sa.Column(sa.UnicodeText)

            caption = sa.Column(sa.UnicodeText)

        class Article(TextItem):
            __tablename__ = 'article'
            id = sa.Column(
                sa.Integer, sa.ForeignKey(TextItem.id), primary_key=True
            )
            __mapper_args__ = {'polymorphic_identity': u'article'}
            category = sa.Unicode(255)

        self.TextItem = TextItem
        self.Article = Article

    def test_auto_creates_relations(self):
        # textitem = self.TextItem()
        # assert textitem.translations
        # assert textitem._translations
        article = self.Article()
        assert article.translations

    def test_auto_creates_current_translation(self):
        # textitem = self.TextItem()
        # assert textitem.current_translation
        article = self.Article()
        assert article.current_translation

    def test_translatable_attributes(self):
        textitem = self.TextItem()
        class_ = textitem.__translatable__['class']
        assert class_.__name__ == 'TextItemTranslation'

    def test_inherits_child_properties(self):
        assert self.Article.caption

    def test_table_name(self):
        article = self.Article()
        table = article.__translatable__['class'].__table__
        assert table.name == 'text_item_translation'

    def test_translated_columns(self):
        article = self.Article()
        columns = sa.inspect(article.__translatable__['class']).columns
        assert 'caption' in columns
        assert 'name' in columns
        assert 'content' in columns
        assert 'description' not in columns

    def test_inherits_parent_table(self):
        table = self.Article.__translatable__['class'].__table__
        assert table == self.TextItem.__translatable__['class'].__table__

    def test_property_delegators(self):
        article = self.Article()
        article.translations['en']

        assert not article.name
        article.current_translation.name = u'something'
        assert article.name == u'something'
        article.name = u'some other thing'
        assert article.current_translation.name == u'some other thing'
        assert article.translations['en'].name == u'some other thing'
        article.caption = u'some caption'
        assert article.current_translation.caption == u'some caption'
