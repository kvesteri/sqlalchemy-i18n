from copy import copy
from inspect import isclass
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


def parent_classes(cls):
    """
    Simple recursive function for listing the parent classes of given class.
    """
    list_of_parents = []
    for parent in cls.__bases__:
        list_of_parents.append(parent)
        list_of_parents.extend(parent_classes(parent))
    return list_of_parents


def all_translated_columns(model):
    columns = set()
    for cls in parent_classes(model) + [model]:
        if hasattr(cls, '__translated_columns__'):
            for column in cls.__translated_columns__:
                columns.add(column)
    return columns


class TranslationManager(object):
    def __init__(self):
        self.class_map = {}
        self.pending_classes = []
        self.options = {
            'locales': [],
            'auto_create_locales': True,
            'base_classes': None,
            'table_name': '%s_translation',
            'locale_column_name': 'locale',
            'default_locale': 'en',
            'get_locale_fallback': False
        }

    def instrument_translatable_classes(self, mapper, cls):
        if issubclass(cls, Translatable):
            if (not cls.__translatable__.get('class')
                    and cls not in self.pending_classes):
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
            self.build_relationships(cls)

    def closest_generated_parent(self, model):
        for class_ in model.__bases__:
            if class_ in self.class_map:
                return self.class_map[class_]

    def option(self, model, name):
        """
        Returns the option value for given model. If the option is not found
        from given model falls back to default values of this manager object.
        If the option is not found from this manager object either this method
        throws a KeyError.

        :param model: SQLAlchemy declarative object
        :param name: name of the translation option
        """
        try:
            return model.__translatable__[name]
        except (AttributeError, KeyError):
            return self.options[name]

    def build_relationships(self, model):
        """
        Build translation relationships for given SQLAlchemy declarative model.

        :param model: SQLAlchemy declarative model
        """
        translation_cls = model.__translatable__['class']
        for locale in self.option(model, 'locales'):
            setattr(
                model,
                '_translation_%s' % locale,
                sa.orm.relationship(
                    translation_cls,
                    primaryjoin=sa.and_(
                        model.id == translation_cls.id,
                        translation_cls.locale == locale
                    ),
                    foreign_keys=[model.id],
                    uselist=False,
                    viewonly=True
                )
            )

        setattr(
            translation_cls,
            'translation_parent',
            sa.orm.relationship(
                model,
                uselist=False,
                cascade='all',
            )
        )

    def set_not_nullables_to_empty_strings(self, locale, obj):
        for column in all_translated_columns(obj.__class__):
            if (
                not column.nullable and
                is_string(column.type) and
                column.default is None and
                column.server_default is None and
                getattr(obj.translations[locale], column.name) is None
            ):
                setattr(obj.translations[locale], column.name, u'')

    def create_missing_locales(self, obj):
        """
        Creates empty locale objects for given SQLAlchemy declarative object.

        :param model: SQLAlchemy declarative model object
        """
        session = sa.orm.session.object_session(obj)
        for locale in self.option(obj, 'locales'):
            if obj.translations[locale] is None:
                class_ = obj.__translatable__['class']
                obj.translations[locale] = class_(
                    translation_parent=obj,
                    locale=locale
                )
            self.set_not_nullables_to_empty_strings(locale, obj)
            session.add(obj)

    def auto_create_translations(self, session, flush_context, instances):
        if not self.options['auto_create_locales']:
            return
        for obj in session.new:
            if hasattr(obj, '__translatable__'):
                self.create_missing_locales(obj)


translation_manager = TranslationManager()


def is_string(type_):
    return (
        isinstance(type_, sa.String) or
        (isclass(type_) and issubclass(type_, sa.String))
    )
