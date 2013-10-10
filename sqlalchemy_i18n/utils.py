from inspect import isclass
import sqlalchemy as sa


def default_locale(obj):
    class_ = obj.__class__
    manager = class_.__translatable__['manager']
    locale = manager.option(class_, 'default_locale')
    if callable(locale):
        locale = locale()
    return locale


def leaf_classes(classes):
    for cls in classes:
        found = False
        for other_cls in classes:
            if issubclass(other_cls, cls) and other_cls is not cls:
                found = True
                break
        if not found:
            yield cls


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
    columns = set()
    for cls in parent_classes(model) + [model]:
        if hasattr(cls, '__translated_columns__'):
            for column in cls.__translated_columns__:
                columns.add(column)
    return columns


def is_string(type_):
    return (
        isinstance(type_, sa.String) or
        (isclass(type_) and issubclass(type_, sa.String))
    )
