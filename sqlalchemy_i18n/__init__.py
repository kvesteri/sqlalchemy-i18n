from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import mapper, relationship  # , attributes, object_mapper
from sqlalchemy.orm.collections import attribute_mapped_collection
# from sqlalchemy.orm.exc import UnmappedColumnError
# from sqlalchemy.orm.interfaces import SessionExtension
from sqlalchemy import Table, Column, ForeignKeyConstraint, Unicode


def col_references_table(col, table):
    for fk in col.foreign_keys:
        if fk.references(table):
            return True
    return False


def _translation_mapper(local_mapper):
    cls = local_mapper.class_

    if not cls.__translated_columns__:
        raise Exception(
            'Transletable models must have __translated_columns__'
            ' attribute defined.'
        )

    super_mapper = local_mapper.inherits
    super_translation_mapper = getattr(cls, '__history_mapper__', None)

    polymorphic_on = None
    super_fks = []
    if (not super_mapper or
            local_mapper.local_table is not super_mapper.local_table):
        cols = []
        for column in local_mapper.local_table.c:
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
        # been added and add them to the history table.
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
    versioned_cls = type.__new__(
        type, "%sTranslation" % cls.__name__, bases, {}
    )

    m = mapper(
        versioned_cls,
        table,
        inherits=super_translation_mapper,
        polymorphic_on=polymorphic_on,
        polymorphic_identity=local_mapper.polymorphic_identity
    )
    cls.__translation_mapper__ = m

    local_mapper.add_property(
        '_translations',
        relationship(
            versioned_cls,
            primaryjoin=getattr(cls, 'id') == getattr(versioned_cls, 'id'),
            collection_class=attribute_mapped_collection('language'),
        )
    )

    def creator(lang, obj):
        obj.language = lang
        return obj

    cls.translations = association_proxy(
        '_translations',
        'language',
        creator=creator
    )


class Translatable(object):
    @declared_attr
    def __mapper_cls__(cls):
        def map(cls, *arg, **kw):
            mp = mapper(cls, *arg, **kw)
            _translation_mapper(mp)
            return mp
        return map


def translated_session(session, locale='en'):
    session.locale = locale
    return session
