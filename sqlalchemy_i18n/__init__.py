import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import mapper, relationship, object_session
from sqlalchemy.orm.collections import (
    MappedCollection, collection
)
from sqlalchemy.orm.util import has_identity
# from sqlalchemy.orm.exc import UnmappedColumnError
# from sqlalchemy.orm.interfaces import SessionExtension
from sqlalchemy import Table, Column, ForeignKeyConstraint, Unicode


class KeyMap(MappedCollection):
    def __init__(self, *args, **kwargs):
        MappedCollection.__init__(self, keyfunc=lambda node: node.language)

    def __getitem__(self, key, _sa_initiator=None):
        if key in self:
            return self.get(key)
        else:
            return None

    @collection.internally_instrumented
    def __setitem__(self, key, value, _sa_initiator=None):
        value.language = key
        super(KeyMap, self).__setitem__(key, value, _sa_initiator)

    @collection.internally_instrumented
    def __delitem__(self, key, _sa_initiator=None):
        super(KeyMap, self).__delitem__(key, _sa_initiator)


def col_references_table(col, table):
    for fk in col.foreign_keys:
        if fk.references(table):
            return True
    return False


def _translation_mapper(local_mapper, translated_columns):
    cls = local_mapper.class_

    super_mapper = local_mapper.inherits
    super_translation_mapper = getattr(cls, '__history_mapper__', None)

    polymorphic_on = None
    super_fks = []
    if (not super_mapper or
            local_mapper.local_table is not super_mapper.local_table):
        cols = []
        for column in (local_mapper.local_table.c + translated_columns):
            if column.name == 'language':
                continue
            if (not column.primary_key
                    and column.name not in cls.__translated_columns__):
                continue

            col = column.copy()
            col.unique = False

            if col.primary_key:
                super_fks.append(
                    (col.key, column)
                )

            cols.append(col)

            if column is local_mapper.polymorphic_on:
                polymorphic_on = col

        cols.append(Column('language', Unicode(5), primary_key=True))

        if super_fks:
            cols.append(ForeignKeyConstraint(*zip(*super_fks)))

        table = Table(
            local_mapper.local_table.name + '_translation',
            local_mapper.local_table.metadata,
            *cols
        )
    else:
        # single table inheritance.  take any additional columns that may have
        # been added and add them to the translation table.
        for column in local_mapper.local_table.c:
            if column.key not in super_translation_mapper.local_table.c:
                col = column.copy()
                col.unique = False
                super_translation_mapper.local_table.append_column(col)
        table = None

    if super_translation_mapper:
        bases = (super_translation_mapper.class_,)
    else:
        bases = local_mapper.base_mapper.class_.__bases__
    translated_cls = type.__new__(
        type, "%sTranslation" % cls.__name__, bases, {}
    )

    m = mapper(
        translated_cls,
        table,
        inherits=super_translation_mapper,
        polymorphic_on=polymorphic_on,
        polymorphic_identity=local_mapper.polymorphic_identity
    )
    cls.__translation_mapper__ = m

    local_mapper.add_property(
        'translations',
        relationship(
            translated_cls,
            primaryjoin=getattr(cls, 'id') == getattr(translated_cls, 'id'),
            backref='parent',
            collection_class=KeyMap,
        )
    )

    for column_name in cls.__translated_columns__:
        def proxy(name):
            def locale_obj(self):
                session = object_session(self)
                locale = get_locale()
                if not session or not has_identity(self):
                    if locale in self.translations:
                        return self.translations[locale]
                    obj = translated_cls(parent=self, language=locale)
                else:
                    try:
                        obj = session.query(translated_cls).filter(
                            sa.and_(
                                translated_cls.id == self.id,
                                translated_cls.language == locale
                            )
                        ).one()
                    except sa.orm.exc.NoResultFound:
                        obj = translated_cls(
                            parent=self, language=locale
                        )
                self.translations[locale] = obj
                return obj

            @property
            def proxy_property(self):
                return getattr(locale_obj(self), name)

            @proxy_property.setter
            def proxy_property(self, value):
                setattr(locale_obj(self), name, value)
            return proxy_property
        setattr(cls, column_name, proxy(column_name))


def get_locale():
    return u'en'


class Translatable(object):
    @declared_attr
    def __mapper_cls__(cls):
        def _map(cls, *args, **kwargs):
            if not cls.__translated_columns__:
                raise Exception(
                    'Translateable models must have __translated_columns__'
                    ' attribute defined.'
                )
            translated_columns = []
            for table in args:
                if isinstance(table, sa.Table):
                    for column in table.c:
                        if column.name in cls.__translated_columns__:
                            translated_columns.append(column)
            mp = mapper(cls, *args, **kwargs)
            _translation_mapper(mp, translated_columns)
            return mp
        return _map


def translated_session(session, locale='en'):
    session.locale = locale
    return session
