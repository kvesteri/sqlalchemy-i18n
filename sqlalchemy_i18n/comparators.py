from sqlalchemy.orm.relationships import RelationshipProperty

from .exc import UnknownLocaleError


class TranslationComparator(RelationshipProperty.Comparator):
    def __getitem__(self, key):
        return getattr(self._parentmapper.class_, '_translation_%s' % key)

    def __getattr__(self, locale):
        class_ = self._parentmapper.class_
        try:
            return getattr(class_, '_translation_%s' % locale)
        except AttributeError:
            raise UnknownLocaleError(locale, class_)
