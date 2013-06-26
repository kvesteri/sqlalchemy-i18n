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
    session=sa.orm.session.Session,
    manager=translation_manager
):
    sa.event.listen(
        mapper, 'instrument_class', manager.instrument_translatable_classes
    )
    sa.event.listen(
        mapper, 'after_configured', manager.configure_translatable_classes
    )
    # Translation ProxyDicts are expired between before_flush and after_flush
    # (ProxyDict emptying is being invoked by object expire event). In
    # order to be able to check if given translation object exists we have to
    # listen to before_flush rather than after_flush.
    sa.event.listen(
        session, 'before_flush', manager.auto_create_translations
    )
