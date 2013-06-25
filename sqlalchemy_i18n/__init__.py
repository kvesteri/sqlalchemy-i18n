import sqlalchemy as sa
from .manager import translation_manager, TranslationManager
from .translatable import Translatable


__all__ = (
    Translatable,
    TranslationManager,
    translation_manager
)


def make_translatable(
    mapper=sa.orm.mapper,
    manager=translation_manager
):
    sa.event.listen(
        mapper, 'instrument_class', manager.instrument_translatable_classes
    )
    sa.event.listen(
        mapper, 'after_configured', manager.configure_translatable_classes
    )
