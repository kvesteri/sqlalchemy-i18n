from contextlib import contextmanager
import six
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.util import has_identity
from .exc import UnknownLocaleError
from .utils import default_locale, option


class Translatable(object):
    __translatable__ = {
        'default_locale': 'en'
    }
    _forced_locale = None

    def get_locale(self):
        raise NotImplementedError(
            'Your translatable model needs to define get_locale method.'
        )

    @contextmanager
    def force_locale(self, locale):
        if locale not in option(self, 'locales'):
            raise UnknownLocaleError(locale, self)
        old_forced_locale = self._forced_locale
        self._forced_locale = locale
        yield
        self._forced_locale = old_forced_locale

    def _get_locale(self):
        locale = self._forced_locale or self.get_locale()
        if locale:
            return locale
        return default_locale(self)

    @hybrid_property
    def current_translation(self):
        locale = six.text_type(self._get_locale())
        return self.translations[locale]

    @current_translation.setter
    def current_translation(self, obj):
        locale = six.text_type(self._get_locale())
        obj.locale = locale
        obj.translation_parent = self
        self._translations[locale] = obj

    @current_translation.expression
    def current_translation(cls):
        if option(cls, 'dynamic_source_locale'):
            return cls._current_translation

        locale = six.text_type(
            six.get_unbound_function(cls.get_locale)(cls)
        )
        return getattr(cls, '_translation_%s' % locale)

    @hybrid_property
    def translations(self):
        if not hasattr(self, '_translations_mapping'):
            self._translations_mapping = TranslationsMapping(self)
        return self._translations_mapping

    @translations.expression
    def translations(self):
        return self._translations


class TranslationsMapping(object):
    def __init__(self, obj):
        self.obj = obj
        self.manager = self.obj.__translatable__['manager']

    def __contains__(self, locale):
        return locale in self.manager.option(self.obj, 'locales')

    def format_key(self, locale):
        return '_translation_%s' % locale

    def fetch(self, locale):
        session = sa.orm.object_session(self.obj)
        # If the object has identity and its in session, get the locale
        # object from the relationship.
        if not session or not has_identity(self.obj):
            return self.obj._translations.get(locale)
        return session.query(self.obj.__translatable__['class']).get(
            (self.obj.id, locale)
        )

    def __getitem__(self, locale):
        if locale in self:
            locale_obj = self.fetch(locale)
            if locale_obj:
                return locale_obj

            class_ = self.obj.__translatable__['class']
            locale_obj = class_(
                translation_parent=self.obj,
                locale=locale
            )
            self.obj._translations[locale] = locale_obj
            return locale_obj
        raise UnknownLocaleError(locale, self.obj)

    def __getattr__(self, locale):
        return self.__getitem__(locale)

    @property
    def all(self):
        return list(self.values())

    def values(self):
        for locale in self.manager.option(self.obj, 'locales'):
            yield self[locale]

    def __setitem__(self, locale, obj):
        if locale in self:
            setattr(self.obj, self.format_key(locale), obj)

    def items(self):
        return [
            (locale, self[locale])
            for locale in self.manager.option(self.obj, 'locales')
        ]

    def iteritems(self):
        for locale in self.manager.option(self.obj, 'locales'):
            yield locale, self[locale]

    def __iter__(self):
        for locale in self.manager.option(self.obj, 'locales'):
            yield locale, self[locale]
