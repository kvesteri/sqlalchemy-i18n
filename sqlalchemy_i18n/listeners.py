import sqlalchemy as sa
from .translatable import Translatable
from .builders import (
    TranslationModelBuilder, TranslationTableBuilder, HybridPropertyBuilder
)


def make_translatable(mapper):
    sa.event.listen(
        mapper, 'instrument_class', instrument_translatable_classes
    )
    sa.event.listen(
        mapper, 'after_configured', configure_translatable_classes
    )


def instrument_translatable_classes(mapper, cls):
    if issubclass(cls, Translatable):
        if (not cls.__translatable__.get('class')
                and cls not in cls.__pending_translatables__):
            cls.__pending_translatables__.append(cls)


def configure_translatable_classes():
    tables = {}

    for cls in Translatable.__pending_translatables__:
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

    for cls in Translatable.__pending_translatables__:
        if cls in tables:
            builder = TranslationModelBuilder(cls)
            builder(tables[cls])
        builder = HybridPropertyBuilder(cls)
        builder()

    Translatable.__pending_translatables__ = []
