import sqlalchemy as sa
from sqlalchemy_i18n import Translatable, translation_manager
from tests import TestCase


class TestTranslationAutoCreation(TestCase):
    def setup_method(self, method):
        TestCase.setup_method(self, method)
        translation_manager.options['auto_created_locales'] = [u'fi', u'en']

    def teardown_method(self, method):
        TestCase.teardown_method(self, method)
        translation_manager.options['auto_created_locales'] = []

    def test_auto_creates_translation_objects(self):
        article = self.Article(name=u'Some article')
        self.session.add(article)
        self.session.commit()

        assert 'en' in article.translations
        assert article.translations['en']
        assert 'fi' in article.translations
        assert article.translations['fi']


class TestTranslationAutoCreationWithNonNullables(TestCase):
    def setup_method(self, method):
        TestCase.setup_method(self, method)
        translation_manager.options['auto_created_locales'] = [u'fi', u'en']

    def teardown_method(self, method):
        TestCase.teardown_method(self, method)
        translation_manager.options['auto_created_locales'] = []

    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translated_columns__ = [
                sa.Column('name', sa.Unicode(255), nullable=False),
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
            discriminator = sa.Column(sa.Unicode(255))

            __mapper_args__ = {
                'polymorphic_on': discriminator,
            }

        class ExtendedArticle(Article):
            __tablename__ = 'extended_article'
            __translated_columns__ = [
                sa.Column('content2', sa.UnicodeText, nullable=False)
            ]
            __mapper_args__ = {'polymorphic_identity': u'extended'}
            id = sa.Column(
                sa.Integer, sa.ForeignKey(Article.id), primary_key=True
            )

        self.Article = Article
        self.ExtendedArticle = ExtendedArticle

    def test_auto_sets_nullables_as_empty_strings(self):
        article = self.ExtendedArticle(
            name=u'Some article',
            content2=u'Some content'
        )
        self.session.add(article)
        self.session.commit()
