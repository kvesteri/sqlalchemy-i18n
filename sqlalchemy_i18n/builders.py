from copy import copy

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy_utils.functions import get_primary_keys

from .comparators import TranslationComparator
from .exc import ImproperlyConfigured
from .expressions import current_locale
from .utils import get_fallback_locale, option


class HybridPropertyBuilder(object):
    def __init__(self, manager, translation_model):
        self.manager = manager
        self.translation_model = translation_model
        self.model = self.translation_model.__parent_class__

    def getter_factory(self, property_name):
        def attribute_getter(obj):
            value = getattr(obj.current_translation, property_name)
            if value:
                return value

            locale = get_fallback_locale(obj)
            return getattr(
                obj.translations[locale],
                property_name
            )

        return attribute_getter

    def setter_factory(self, property_name):
        """
        Return a hybrid property setter for given property name.

        :param property_name: Name of the property to generate a setter for
        """
        return (
            lambda obj, value:
            setattr(obj.current_translation, property_name, value)
        )

    def generate_hybrid(self, property_name):
        """
        Generate a SQLAlchemy hybrid property for given translation model
        property.

        :param property_name:
            Name of the translation model property to generate hybrid property
            for.
        """
        setattr(
            self.model,
            property_name,
            hybrid_property(
                fget=self.getter_factory(property_name),
                fset=self.setter_factory(property_name),
                expr=lambda cls: getattr(
                    cls.__translatable__['class'], property_name
                )
            )
        )

    def detect_collisions(self, property_name):
        """
        Detect possible naming collisions for given property name.

        :raises sqlalchemy_i18n.exc.ImproperlyConfigured: if the model already
            has a property with given name
        """
        mapper = sa.inspect(self.model)
        if mapper.has_property(property_name):
            raise ImproperlyConfigured(
                "Attribute name collision detected. Could not create "
                "hybrid property for translated attribute '%s'. "
                "An attribute with the same already exists in parent "
                "class '%s'." % (
                    property_name,
                    self.model.__name__
                )
            )

    def __call__(self):
        mapper = sa.orm.class_mapper(self.translation_model)
        for column in mapper.local_table.c:
            exclude = self.manager.option(
                self.model, 'exclude_hybrid_properties'
            )

            if column.key in exclude or column.primary_key:
                continue

            self.detect_collisions(column.key)
            self.generate_hybrid(column.key)


class RelationshipBuilder(object):
    def __init__(self, manager, translation_cls):
        self.manager = manager
        self.translation_cls = translation_cls
        self.parent_cls = self.translation_cls.__parent_class__

    @property
    def primary_key_conditions(self):
        conditions = []
        for key in get_primary_keys(self.parent_cls).keys():
            conditions.append(
                getattr(self.parent_cls, key) ==
                getattr(self.translation_cls, key)
            )
        return conditions

    def assign_single_translations(self):
        mapper = sa.orm.class_mapper(self.parent_cls)
        for locale in option(self.parent_cls, 'locales'):
            key = '_translation_%s' % locale
            if mapper.has_property(key):
                continue

            conditions = self.primary_key_conditions
            conditions.append(self.translation_cls.locale == locale)
            mapper.add_property(key, sa.orm.relationship(
                self.translation_cls,
                primaryjoin=sa.and_(*conditions),
                foreign_keys=list(
                    get_primary_keys(self.parent_cls).values()
                ),
                uselist=False,
                viewonly=True
            ))

    def assign_fallback_translation(self):
        """
        Assign the current translation relationship for translatable parent
        class.
        """
        mapper = sa.orm.class_mapper(self.parent_cls)
        if not mapper.has_property('_fallback_translation'):
            conditions = self.primary_key_conditions
            conditions.append(
                self.translation_cls.locale ==
                get_fallback_locale(self.parent_cls)
            )

            mapper.add_property('_fallback_translation', sa.orm.relationship(
                self.translation_cls,
                primaryjoin=sa.and_(*conditions),
                foreign_keys=list(
                    get_primary_keys(self.parent_cls).values()
                ),
                viewonly=True,
                uselist=False
            ))

    def assign_current_translation(self):
        """
        Assign the current translation relationship for translatable parent
        class.
        """
        mapper = sa.orm.class_mapper(self.parent_cls)
        if not mapper.has_property('_current_translation'):
            conditions = self.primary_key_conditions
            conditions.append(
                self.translation_cls.locale == current_locale()
            )

            mapper.add_property('_current_translation', sa.orm.relationship(
                self.translation_cls,
                primaryjoin=sa.and_(*conditions),
                foreign_keys=list(
                    get_primary_keys(self.parent_cls).values()
                ),
                viewonly=True,
                uselist=False
            ))

    def assign_translations(self):
        """
        Assigns translations relationship for translatable model. The assigned
        attribute is a relationship to all translation locales.
        """
        mapper = sa.orm.class_mapper(self.parent_cls)
        if not mapper.has_property('_translations'):
            mapper.add_property('_translations', sa.orm.relationship(
                self.translation_cls,
                **self.get_translations_relationship_args()
            ))

    def get_translations_relationship_args(self):
        foreign_keys = [
            getattr(self.translation_cls, column_key)
            for column_key in get_primary_keys(self.parent_cls).keys()
        ]

        relationship_args = copy(
            self.manager.option(
                self.parent_cls,
                'translations_relationship_args'
            )
        )
        defaults = dict(
            primaryjoin=sa.and_(*self.primary_key_conditions),
            foreign_keys=foreign_keys,
            collection_class=attribute_mapped_collection('locale'),
            comparator_factory=TranslationComparator,
            cascade='all, delete-orphan',
            passive_deletes=True,
        )
        for key, value in defaults.items():
            relationship_args.setdefault(key, value)
        return relationship_args

    def assign_translation_parent(self):
        mapper = sa.orm.class_mapper(self.translation_cls)
        if not mapper.has_property('translation_parent'):
            mapper.add_property('translation_parent', sa.orm.relationship(
                self.parent_cls,
                uselist=False,
                viewonly=True
            ))

    def __call__(self):
        self.assign_single_translations()
        self.assign_current_translation()
        self.assign_fallback_translation()
        self.assign_translations()
        self.assign_translation_parent()
