import sqlalchemy as sa
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles


class current_locale(expression.FunctionElement):
    type = sa.types.Unicode()
    name = 'current_locale'


@compiles(current_locale)
def compile_current_locale(element, compiler, **kw):
    # Lazy import get_locale so that it can be overridden
    from sqlalchemy_utils.i18n import get_locale

    return '%s' % compiler.process(
        sa.bindparam('current_locale', str(get_locale()))
    )
