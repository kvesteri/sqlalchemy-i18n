from inspect import isclass
import sqlalchemy as sa


def option(obj_or_class, option):
    class_ = obj_or_class if isclass(obj_or_class) else obj_or_class.__class__
    manager = class_.__translatable__['manager']
    return manager.option(class_, option)


def default_locale(obj):
    class_ = obj.__class__
    manager = class_.__translatable__['manager']
    locale = manager.option(class_, 'default_locale')
    if callable(locale):
        locale = locale()
    return locale


def parent_classes(cls):
    """
    Simple recursive function for listing the parent classes of given class.
    """
    list_of_parents = []
    for parent in cls.__bases__:
        list_of_parents.append(parent)
        list_of_parents.extend(parent_classes(parent))
    return list_of_parents


def all_translated_columns(model):
    for column in sa.inspect(model.__translatable__['class']).columns:
        if not column.primary_key:
            yield column


def is_string(type_):
    return (
        isinstance(type_, sa.String) or
        (isclass(type_) and issubclass(type_, sa.String))
    )
