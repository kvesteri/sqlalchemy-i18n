from inspect import isclass

import sqlalchemy as sa


def get_current_locale(obj):
    from sqlalchemy_utils import i18n

    locale = i18n.get_locale()
    if locale:
        return str(locale)
    return obj.locale


def get_fallback_locale(obj):
    manager = obj.__translatable__['manager']

    locale = manager.option(obj, 'fallback_locale')
    if callable(locale):
        locale = locale(obj)
    return locale


def option(obj_or_class, option):
    class_ = obj_or_class if isclass(obj_or_class) else obj_or_class.__class__
    manager = class_.__translatable__['manager']
    return manager.option(class_, option)


def all_translated_columns(model):
    for column in sa.inspect(model.__translatable__['class']).columns:
        if not column.primary_key:
            yield column


def is_string(type_):
    return (
        isinstance(type_, sa.String) or
        (isclass(type_) and issubclass(type_, sa.String))
    )
