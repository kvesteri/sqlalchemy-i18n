import sqlalchemy as sa
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declared_attr, has_inherited_table
from sqlalchemy_utils.functions import declarative_base, primary_keys

from .builders import HybridPropertyBuilder
from .exc import UnknownLocaleError
from .utils import all_translated_columns, is_string



class TranslationComparator(RelationshipProperty.Comparator):
    def __getitem__(self, key):
        return getattr(self._parentmapper.class_, '_translation_%s' % key)

    def __getattr__(self, locale):
        class_ = self._parentmapper.class_
        try:
            return getattr(class_, '_translation_%s' % locale)
        except AttributeError:
            raise UnknownLocaleError(locale, class_)


class_map = {}


class BaseTranslationMixin(object):
    pass


def translation_base(parent_cls):
    class TranslationMixin(
        declarative_base(parent_cls),
        BaseTranslationMixin
    ):
        __abstract__ = True
        __parent_class__ = parent_cls

        @declared_attr
        def __table_args__(cls):
            if has_inherited_table(cls):
                return tuple()
            else:
                names = [column.name for column in primary_keys(parent_cls)]

                return (sa.schema.ForeignKeyConstraint(
                    names,
                    [
                        '%s.%s' % (parent_cls.__tablename__, name)
                        for name in names
                    ],
                    ondelete='CASCADE'
                ), )

    for column in parent_cls.__table__.c:
        if column.primary_key:
            setattr(
                TranslationMixin,
                column.key,
                column.copy()
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
            'default_locale': 'en',
            'exclude_hybrid_properties': []
        }

    def instrument_translatable_classes(self, mapper, cls):
        if issubclass(cls, BaseTranslationMixin):
            self.pending_classes.append(cls)

    def configure_translatable_classes(self):
        for cls in self.pending_classes:
            self.class_map[cls.__parent_class__] = cls
            parent_cls = cls.__parent_class__
            parent_cls.__translatable__['manager'] = self
            parent_cls.__translatable__['class'] = cls

            builder = HybridPropertyBuilder(self, cls)
            builder()

            self.build_relationships(cls)
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

    def build_relationships(self, translation_cls):
        """
        Build translation relationships for given SQLAlchemy declarative model.

        :param model: SQLAlchemy declarative model
        """
        model = translation_cls.__parent_class__
        for locale in self.option(model, 'locales'):
            key = '_translation_%s' % locale
            if key in model.__dict__:
                continue
            setattr(
                model,
                key,
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

        if not hasattr(model, '_translations'):
            model._translations = sa.orm.relationship(
                translation_cls,
                primaryjoin=model.id == translation_cls.id,
                foreign_keys=[translation_cls.id],
                collection_class=attribute_mapped_collection('locale'),
                comparator_factory=TranslationComparator,
                cascade='all, delete-orphan',
                passive_deletes=True,
            )

        try:
            current_locale = model.locale
        except NotImplementedError:
            pass
        else:
            if '_current_translation' not in model.__dict__:
                model._current_translation = sa.orm.relationship(
                    translation_cls,
                    primaryjoin=sa.and_(
                        model.id == translation_cls.id,
                        translation_cls.locale == current_locale,
                    ),
                    foreign_keys=[model.id],
                    viewonly=True,
                    uselist=False
                )

        if 'translation_parent' not in translation_cls.__dict__:
            setattr(
                translation_cls,
                'translation_parent',
                sa.orm.relationship(
                    model,
                    uselist=False,
                    viewonly=True
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
