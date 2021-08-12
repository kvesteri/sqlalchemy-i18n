from copy import copy
from sqlalchemy_i18n.i18n_id_column import I18IdColumn

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr, has_inherited_table
from sqlalchemy_utils.functions import get_declarative_base, get_primary_keys

from .builders import HybridPropertyBuilder, RelationshipBuilder
from .utils import all_translated_columns, is_string, get_pk_column


class BaseTranslationMixin(object):
    pass


def translation_base(
    parent_cls,
    base_class_factory=None,
    foreign_key_args=None,
    create_columns=True
):
    if base_class_factory is None:
        base_class_factory = get_declarative_base

    if foreign_key_args is None:
        foreign_key_args = {}
        foreign_key_args.setdefault('ondelete', 'CASCADE')

    class TranslationMixin(
        base_class_factory(parent_cls),
        BaseTranslationMixin
    ):
        __abstract__ = True
        __parent_class__ = parent_cls

        @declared_attr
        def __table_args__(cls):
            if has_inherited_table(cls):
                return tuple()
            else:
                if any(isinstance(getattr(cls, c), I18IdColumn) for c in dir(cls) if '__' not in c):
                    return create_i18n_fk_constraint(cls, parent_cls, foreign_key_args)
    
                names = list(get_primary_keys(parent_cls).keys())

                return (
                    sa.schema.ForeignKeyConstraint(
                        names,
                        [
                            '%s.%s' % (parent_cls.__tablename__, name)
                            for name in names
                        ],
                        **foreign_key_args
                    ),
                )

    if create_columns:
        for column in parent_cls.__table__.c:
            if column.primary_key:
                column_copy = column._copy()
                column_copy.autoincrement = False
                setattr(
                    TranslationMixin,
                    column.key,
                    column_copy
                )

    TranslationMixin.locale = sa.Column(
        sa.String(10), primary_key=True
    )

    return TranslationMixin


class TranslationManager(object):
    def __init__(self):
        self.class_map = {}
        self.pending_classes = []
        self.options = {
            'locales': [],
            'auto_create_locales': True,
            'fallback_locale': 'en',
            'exclude_hybrid_properties': [],
            'translations_relationship_args': {},
            'fallback_to_parent': False,
        }

    def instrument_translation_classes(self, mapper, cls):
        """
        SQLAlchemy class instrumentation listener that adds all translation
        classes to pending classes list. These classes are later on processed
        by configure_translatable_classes listener.

        :param mapper: SQLAlchemy mapper
        :param cls: SQLAlchemy declarative class
        """
        if issubclass(cls, BaseTranslationMixin):
            self.pending_classes.append(cls)

    def configure_translatable_classes(self):
        """
        This SQLAlchemy after_configured listener configures all translation
        classes, builds hybrid properties for translation parent classes and
        finally builds relationships between translation and parent classes.
        """
        for cls in self.pending_classes:
            self.class_map[cls.__parent_class__] = cls
            parent_cls = cls.__parent_class__
            # Args need to be copied to avoid scenarios where many child
            # classes inherit the __translatable__ dict from parent class and
            # then have the same reference to same dict.
            parent_cls.__translatable__ = copy(parent_cls.__translatable__)
            parent_cls.__translatable__['manager'] = self
            parent_cls.__translatable__['class'] = cls

            HybridPropertyBuilder(self, cls)()
            RelationshipBuilder(self, cls)()

        self.pending_classes = []

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
        if self.options['auto_create_locales']:
            for obj in session.new:
                if hasattr(obj, '__translatable__'):
                    self.create_missing_locales(obj)

def create_i18n_fk_constraint(cls, parent_cls, foreign_key_args):
    cols = [getattr(cls, c) for c in dir(cls) if '__' not in c and isinstance(getattr(cls, c), I18IdColumn)]
    return (
        sa.schema.ForeignKeyConstraint(
            [col.key for col in cols] ,
            [
                '%s.%s' % (parent_cls.__tablename__, col.rn_parent_col)
                for col in cols
            ],
            **foreign_key_args
        ),
    )

translation_manager = TranslationManager()
