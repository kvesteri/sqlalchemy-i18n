import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property


class ImproperlyConfigured(Exception):
    pass


class TranslationBuilder(object):
    def __init__(self, manager, translation_model):
        self.manager = manager
        self.translation_model = translation_model
        self.model = self.translation_model.__parent_class__

    def option(self, name):
        try:
            return self.model.__translatable__[name]
        except (AttributeError, KeyError):
            return self.manager.options[name]


class HybridPropertyBuilder(TranslationBuilder):
    def getter_factory(self, name):
        def attribute_getter(obj):
            value = getattr(obj.current_translation, name)
            if value:
                return value

            default_locale = self.manager.option(obj, 'default_locale')
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
        if not mapper.has_property(column_name):
            return

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


# class TranslationModelBuilder(TranslationBuilder):
#     def build_foreign_key(self):
#         names = [column.name for column in primary_keys(self.model)]
#         return sa.schema.ForeignKeyConstraint(
#             names,
#             [
#                 '%s.%s' % (self.model.__tablename__, name)
#                 for name in names
#             ],
#             ondelete='CASCADE'
#         )

#     @property
#     def base_classes(self):
#         parent = self.manager.closest_generated_parent(self.model)
#         parent = (parent, ) if parent else None
#         return (
#             parent
#             or self.option('base_classes')
#             or (declarative_base(self.model), )
#         )

#     def build_model(self):
#         data = {}
#         if not self.manager.closest_generated_parent(self.model):
#             data.update({
#                 '__table_args__': (self.build_foreign_key(), ),
#                 '__tablename__': self.table_name,
#             })
#         data.update(self.columns)
#         return type(
#             '%sTranslation' % self.model.__name__,
#             self.base_classes,
#             data
#         )

#     def __call__(self):
#         # translatable attributes need to be copied for each child class,
#         # otherwise each child class would share the same __translatable__
#         # option dict
#         if not self.option('locales'):
#             raise ImproperlyConfigured(
#                 'Either the translation manager or the model class must define'
#                 ' available locales as a configuration option.'
#             )

#         self.model.__translatable__ = copy(self.model.__translatable__)
#         self.translation_class = self.build_model()
#         self.model.__translatable__['class'] = self.translation_class
#         self.model.__translatable__['manager'] = self.manager
#         self.translation_class.__parent_class__ = self.model
#         return self.translation_class
