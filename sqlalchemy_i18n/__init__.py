import sqlalchemy as sa

from .builders import ImproperlyConfigured
from .manager import translation_base, translation_manager, TranslationManager
from .translatable import Translatable, UnknownLocaleError

__all__ = (
    translation_base,
    ImproperlyConfigured,
    Translatable,
    TranslationManager,
    translation_manager,
    UnknownLocaleError
)


__version__ = '1.0.3'


def make_translatable(
    mapper=sa.orm.mapper,
    session=sa.orm.session.Session,
    manager=translation_manager,
    options={}
):
    """
    Assigns translation listeners for given mapper and session.

    :param mapper:
        SQLAlchemy declarative class or mapper to apply translation listeners
        into.
    :param session:
        SQLAlchemy session class.
    :param manager:
        SQLAlchemy-i18n TranslationManager instance
    :param options:
        TranslationManager options
    """
    manager.options.update(options)

    sa.event.listen(
        mapper, 'instrument_class', manager.instrument_translation_classes
    )
    sa.event.listen(
        mapper, 'after_configured', manager.configure_translatable_classes
    )
    sa.event.listen(
        session, 'before_flush', manager.auto_create_translations
    )


def find_translations(obj, property_name, locale):
    class_ = obj.__class__
    session = sa.orm.object_session(obj)
    translation_class = class_.__translatable__['class']

    property_ = getattr(translation_class, property_name)

    subquery = (
        session.query(translation_class.id)
        .filter(
            sa.and_(
                property_ ==
                getattr(obj, property_name),
                translation_class.locale ==
                obj.locale
            )
        )
    )

    conditions = [
        translation_class.id.in_(subquery),
        translation_class.locale == locale,
        property_.isnot(None)
    ]

    total_count = (
        session.query(sa.func.cast(sa.func.count('1'), sa.Numeric))
        .filter(sa.and_(*conditions))
    )

    query = (
        session.query(
            property_.label('translation'),
            (sa.func.cast(sa.func.count('1'), sa.Numeric) / total_count)
            .label('confidence')
        )
        .filter(sa.and_(*conditions))
        .group_by(property_)
    )
    return query
