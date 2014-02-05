import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property


class ImproperlyConfigured(Exception):
    pass


class HybridPropertyBuilder(object):
    def __init__(self, manager, translation_model):
        self.manager = manager
        self.translation_model = translation_model
        self.model = self.translation_model.__parent_class__

    def option(self, name):
        try:
            return self.model.__translatable__[name]
        except (AttributeError, KeyError):
            return self.manager.options[name]

    def getter_factory(self, name):
        def attribute_getter(obj):
            value = getattr(obj.current_translation, name)
            if value:
                return value

            default_locale = self.manager.option(obj, 'fallback_locale')
            if callable(default_locale):
                default_locale = default_locale(obj)
            return getattr(
                obj.translations[default_locale],
                name
            )

        return attribute_getter

    def setter_factory(self, name):
        return (
            lambda obj, value:
            setattr(obj.current_translation, name, value)
        )

    def assign_attr_getter_setters(self, attr):
        setattr(
            self.model,
            attr,
            hybrid_property(
                fget=self.getter_factory(attr),
                fset=self.setter_factory(attr),
                expr=lambda cls: getattr(cls.__translatable__['class'], attr)
            )
        )

    def detect_collisions(self, column_name):
        mapper = sa.inspect(self.model)
        if mapper.has_property(column_name):
            raise ImproperlyConfigured(
                "Attribute name collision detected. Could not create "
                "hybrid property for translated attribute '%s'. "
                "An attribute with the same already exists in parent "
                "class '%s'." % (
                    column_name,
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
            self.assign_attr_getter_setters(column.key)
