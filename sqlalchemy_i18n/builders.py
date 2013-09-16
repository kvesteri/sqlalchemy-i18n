from copy import copy
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property, Comparator
from sqlalchemy_utils.functions import primary_keys


class ImproperlyConfigured(Exception):
    pass


def translation_getter_factory(name):
    def attribute_getter(self):
        value = getattr(self.current_translation, name)
        if value:
            return value

        default_locale = self.__translatable__['default_locale']
        if callable(default_locale):
            default_locale = default_locale(self)
        return getattr(
            getattr(self, '_translation_%s' % default_locale),
            name
        )

    return attribute_getter


def translation_setter_factory(name):
    return (
        lambda self, value:
        setattr(self.current_translation, name, value)
    )


class TranslationTransformer(Comparator):
    def __init__(self, cls):
        self.alias = sa.orm.aliased(cls.__translatable__['class'])
        self.parent = cls

    @property
    def join(self):
        def go(q):
            return q.outerjoin(self.alias, self.parent.current_translation)
        return go

    def operate(self, op, other):
        return op(self.alias.name, other)


class TranslationBuilder(object):
    def __init__(self, manager, model):
        self.manager = manager
        self.model = model

    def option(self, name):
        try:
            return self.model.__translatable__[name]
        except (AttributeError, KeyError):
            return self.manager.options[name]


class HybridPropertyBuilder(TranslationBuilder):
    def assign_attr_getter_setters(self, attr):
        setattr(
            self.model,
            attr,
            hybrid_property(
                fget=translation_getter_factory(attr),
                fset=translation_setter_factory(attr),
                expr=lambda cls: getattr(cls.__translatable__['class'], attr)
            )
        )

    def __call__(self):
        for column in self.model.__translated_columns__:
            self.assign_attr_getter_setters(column.key)


class TranslationModelBuilder(TranslationBuilder):
    @property
    def table_name(self):
        return self.option('table_name') % self.model.__tablename__

    def build_reflected_primary_keys(self):
        columns = []
        for column in primary_keys(self.model):
            # Make a copy of the column so that it does not point to wrong
            # table.
            column_copy = column.copy()
            # Remove unique constraints
            column_copy.unique = False
            columns.append(column_copy)
        return columns

    def build_foreign_key(self):
        names = [column.name for column in primary_keys(self.model)]
        return sa.schema.ForeignKeyConstraint(
            names,
            [
                '%s.%s' % (self.model.__tablename__, name)
                for name in names
            ],
            ondelete='CASCADE'
        )

    def build_locale_column(self):
        return sa.Column(
            self.option('locale_column_name'),
            sa.String(10),
            primary_key=True
        )

    @property
    def columns(self):
        columns = []
        if not self.manager.closest_generated_parent(self.model):
            columns.extend(self.build_reflected_primary_keys())
            columns.append(self.build_locale_column())
        columns.extend(self.model.__translated_columns__)
        return dict([(column.name, column) for column in columns])

    @property
    def base_classes(self):
        parent = self.manager.closest_generated_parent(self.model)
        parent = (parent, ) if parent else None
        return (
            parent
            or self.option('base_classes')
            or (self.declarative_base(self.model), )
        )

    def declarative_base(self, model):
        for parent in model.__bases__:
            try:
                parent.metadata
                return self.declarative_base(parent)
            except AttributeError:
                pass
        return model

    def build_model(self):
        data = {}
        if not self.manager.closest_generated_parent(self.model):
            data.update({
                '__table_args__': (self.build_foreign_key(), ),
                '__tablename__': self.table_name,
            })
        data.update(self.columns)
        return type(
            '%sTranslation' % self.model.__name__,
            self.base_classes,
            data
        )

    def __call__(self):
        # translatable attributes need to be copied for each child class,
        # otherwise each child class would share the same __translatable__
        # option dict
        if not self.option('locales'):
            raise ImproperlyConfigured(
                'Either the translation manager or the model class must define'
                ' available locales as a configuration option.'
            )

        self.model.__translatable__ = copy(self.model.__translatable__)
        self.translation_class = self.build_model()
        self.model.__translatable__['class'] = self.translation_class
        self.model.__translatable__['manager'] = self.manager
        self.translation_class.__parent_class__ = self.model
        return self.translation_class
