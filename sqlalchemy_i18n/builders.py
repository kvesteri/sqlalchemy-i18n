import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property

from .exc import ImproperlyConfigured




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

            default_locale = self.manager.option(obj, 'fallback_locale')
            if callable(default_locale):
                default_locale = default_locale(obj)
            return getattr(
                obj.translations[default_locale],
                property_name
            )

        return attribute_getter

    def setter_factory(self, property_name):
        """
        Returns a hybrid property setter for given property name.

        :param property_name: Name of the property to generate a setter for
        """
        return (
            lambda obj, value:
            setattr(obj.current_translation, property_name, value)
        )

    def generate_hybrid(self, property_name):
        """
        Generates a SQLAlchemy hybrid property for given translation model
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
        Detects possible naming collisions for given property name.

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
        for column in self.translation_model.__table__.c:
            exclude = self.manager.option(
                self.model, 'exclude_hybrid_properties'
            )

            if column.key in exclude or column.primary_key:
                continue

            self.detect_collisions(column.key)
            self.generate_hybrid(column.key)
