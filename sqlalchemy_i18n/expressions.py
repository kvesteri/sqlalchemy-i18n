import sqlalchemy as sa
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import GenericFunction


class current_locale(GenericFunction):
    type = sa.types.String()


@compiles(current_locale)
def compile_current_locale(element, compiler, **kw):
    # Lazy import get_locale so that it can be overridden
    from sqlalchemy_utils.i18n import get_locale

    return '%s' % compiler.process(
        sa.bindparam('current_locale', str(get_locale()))
    )
