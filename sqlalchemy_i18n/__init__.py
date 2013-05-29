from copy import copy
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property, Comparator
from sqlalchemy_utils import proxy_dict
from sqlalchemy_utils.functions import primary_keys


class Translatable(object):
    __translatable__ = {}
    __pending__ = []

    def get_locale(self):
        raise NotImplementedError(
            'Your translatable model needs to define get_locale method.'
        )

    @hybrid_property
    def current_translation(self):
        locale = str(self.get_locale())
        if locale in self.translations:
            try:
                self._current_translation = self.translations[locale]
            except AttributeError:
                self.__class__.load_lazy_relationships()
                self._current_translation = self.translations[locale]

            return self.translations[locale]

        class_ = self.__translatable__['class']
        obj = class_()
        obj.locale = locale
        self.translations[locale] = obj
        self._current_translation = obj
        return obj

    @current_translation.setter
    def current_translation(self, obj):
        locale = str(self.get_locale())
        obj.locale = locale
        self.translations[locale] = obj

    @current_translation.expression
    def current_translation(cls):
        try:
            return cls._current_translation
        except AttributeError:
            cls.load_lazy_relationships()
            return cls._current_translation

    @classmethod
    def load_lazy_relationships(cls):
        locale = str(cls.get_locale.im_func(cls))
        translation_cls = cls.__translatable__['class']
        cls._current_translation = sa.orm.relationship(
            translation_cls,
            primaryjoin=sa.and_(
                cls.id == translation_cls.id,
                translation_cls.locale == locale
            ),
            uselist=False,
            viewonly=True
        )

    @hybrid_property
    def translations(self):
        return proxy_dict(
            self,
            '_translations',
            getattr(self.__translatable__['class'], 'locale')
        )

    @translations.expression
    def translations(cls):
        return cls._translations

    @classmethod
    def __declare_last__(cls):
        if not cls.__translatable__.get('class'):
            cls.__pending__.append(cls)


def translation_getter_factory(name):
    return lambda self: getattr(self.current_translation, name)


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


def configure_translatables():
    tables = {}

    for cls in Translatable.__pending__:
        existing_table = None
        for class_ in tables:
            if issubclass(cls, class_):
                existing_table = tables[class_]
                break

        builder = TranslationTableBuilder(cls)
        if existing_table is not None:
            tables[class_] = builder.build_table(existing_table)
        else:
            table = builder.build_table()
            tables[cls] = table

    for cls in Translatable.__pending__:
        if cls in tables:
            builder = TranslationModelBuilder(cls)
            builder(tables[cls])
        builder = HybridPropertyBuilder(cls)
        builder()

    Translatable.__pending__ = []


class TranslationBuilder(object):
    DEFAULT_OPTIONS = {
        'base_classes': None,
        'table_name': '%s_translation',
        'locale_column_name': 'locale',
    }

    def __init__(self, model):
        self.model = model

    def option(self, name):
        try:
            return self.model.__translatable__[name]
        except (AttributeError, KeyError):
            return self.DEFAULT_OPTIONS[name]


class TranslationTableBuilder(TranslationBuilder):
    def __init__(self, model):
        self.model = model

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

    def build_table(self, extends=None):
        items = []
        if extends is None:
            items.extend(self.build_reflected_primary_keys())
            items.append(self.build_locale_column())

        items.extend(self.model.__translated_columns__)

        if extends is None:
            items.append(self.build_foreign_key())

        return sa.schema.Table(
            extends.name if extends is not None else self.table_name,
            self.model.__bases__[0].metadata,
            *items,
            extend_existing=extends is not None
        )


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
            self.assign_attr_getter_setters(column.name)


class TranslationModelBuilder(TranslationBuilder):
    def build_relationship(self):
        self.model._translations = sa.orm.relationship(
            self.translation_class,
            lazy='dynamic',
            cascade='all, delete-orphan',
            passive_deletes=True,
            backref=sa.orm.backref('parent'),
        )

    def build_model(self, table):
        if not self.option('base_classes'):
            raise Exception(
                'Missing __translatable__ base_classes option for model %s.'
                % self.model.__name__
            )
        return type(
            '%sTranslation' % self.model.__name__,
            self.option('base_classes'),
            {'__table__': table}
        )

    def __call__(self, table):
        # translatable attributes need to be copied for each child class,
        # otherwise each child class would share the same __translatable__
        # option dict
        self.model.__translatable__ = copy(self.model.__translatable__)
        self.translation_class = self.build_model(table)
        self.build_relationship()
        self.model.__translatable__['class'] = self.translation_class
        self.translation_class.__parent_class__ = self.model
