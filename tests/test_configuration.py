# -*- coding: utf-8 -*-

import sqlalchemy as sa

from sqlalchemy_i18n import Translatable, translation_base
from tests import DeclarativeTestCase


class TestTranslationBaseCustomization(DeclarativeTestCase):
    def create_models(self):
        class Article(self.Model, Translatable):
            __tablename__ = 'article'
            __translatable__ = {
                'locales': ['fi', 'en'],
                'auto_create_locales': True,
                'translations_relationship_args': {
                    'collection_class': list,
                }
            }

            id = sa.Column(sa.Integer, primary_key=True)

            locale = 'en'

        TranslationBase = translation_base(
            Article,
            foreign_key_args={'onupdate': 'SET NULL'}
        )

        class ArticleTranslation(TranslationBase):
            __tablename__ = 'article_translation'

            name = sa.Column(sa.Unicode(255))

        self.Article = Article
        self.ArticleTranslation = ArticleTranslation

    def test_customize_foreign_key_args(self):
        assert (
            self.ArticleTranslation.__table__.foreign_keys.pop().onupdate ==
            'SET NULL'
        )

    def test_customize_relationships_args(self):
        assert self.Article._translations.property.collection_class == list
