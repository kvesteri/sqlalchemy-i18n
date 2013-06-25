from copy import copy
import sqlalchemy as sa
from .translatable import Translatable
from .builders import (
    TranslationModelBuilder, HybridPropertyBuilder
)


def leaf_classes(classes):
    for cls in classes:
        found = False
        for other_cls in classes:
            if issubclass(other_cls, cls) and other_cls is not cls:
                found = True
                break
        if not found:
            yield cls


class TranslationManager(object):
    def __init__(self):
        self.class_map = {}
        self.pending_classes = []

    def instrument_translatable_classes(self, mapper, cls):
        if issubclass(cls, Translatable):
            if (not cls.__translatable__.get('class')
                    and cls not in cls.__pending_translatables__):
                self.pending_classes.append(cls)

    def configure_translatable_classes(self):
        for cls in self.pending_classes:
            builder = TranslationModelBuilder(self, cls)
            self.class_map[cls] = builder()
            builder = HybridPropertyBuilder(self, cls)
            builder()

        pending_classes_copy = copy(self.pending_classes)
        self.pending_classes = []
        for cls in leaf_classes(pending_classes_copy):
            self.build_relationship(cls)

    def closest_generated_parent(self, model):
        for class_ in model.__bases__:
            if class_ in self.class_map:
                return self.class_map[class_]

    def build_relationship(self, model):
        model._translations = sa.orm.relationship(
            model.__translatable__['class'],
            lazy='dynamic',
            cascade='all, delete-orphan',
            passive_deletes=True,
            backref=sa.orm.backref('parent'),
        )


translation_manager = TranslationManager()
