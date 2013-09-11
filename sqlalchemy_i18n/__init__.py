import sqlalchemy as sa
from .manager import translation_manager, TranslationManager
from .translatable import Translatable


__all__ = (
    Translatable,
    TranslationManager,
    translation_manager
)


__version__ = '0.6.8'


def make_translatable(
    mapper=sa.orm.mapper,
    session=sa.orm.session.Session,
    manager=translation_manager,
    options={}
):
    manager.options.update(options)

    sa.event.listen(
        mapper, 'instrument_class', manager.instrument_translatable_classes
    )
    sa.event.listen(
        mapper, 'after_configured', manager.configure_translatable_classes
    )
    sa.event.listen(
        session, 'before_flush', manager.auto_create_translations
    )
