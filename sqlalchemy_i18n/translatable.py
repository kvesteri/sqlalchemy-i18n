import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.util import has_identity

from .exc import UnknownLocaleError
from .utils import get_current_locale, get_fallback_locale


class Translatable(object):
    __translatable__ = {
        'fallback_locale': 'en'
    }

    @hybrid_property
    def locale(self):
        raise NotImplementedError(
            'Your translatable model needs to define locale property.'
        )

    # Current translation getters and setters
    @hybrid_property
    def current_translation(self):
        return self.translations[get_current_locale(self)]

    @current_translation.setter
    def current_translation(self, obj):
        self.translations[get_current_locale(self)] = obj

    @current_translation.expression
    def current_translation(cls):
        return cls._current_translation

    # Fallback translation getters and setters
    @hybrid_property
    def fallback_translation(self):
        return self.translations[get_fallback_locale(self)]

    @fallback_translation.setter
    def fallback_translation(self, obj):
        self.translations[get_fallback_locale(self)] = obj

    @fallback_translation.expression
    def fallback_translation(cls):
        return cls._fallback_translation

    # Translations getters and setters
    @hybrid_property
    def translations(self):
        if not hasattr(self, '_translations_mapping'):
            self._translations_mapping = TranslationsMapping(self)
        return self._translations_mapping

    @translations.setter
    def translations(self, translations_mapping):
        self._translations = translations_mapping

    @translations.expression
    def translations(self):
        return self._translations


@sa.event.listens_for(sa.orm.mapper, 'expire')
def receive_expire(target, attrs):
    if isinstance(target, Translatable):
        try:
            del target._translations_mapping
        except AttributeError:
            pass


class TranslationsMapping(object):
    def __init__(self, obj):
        self.obj = obj
        self.manager = self.obj.__translatable__['manager']

    def __contains__(self, locale):
        return locale in self.manager.option(self.obj, 'locales')

    def fetch(self, locale):
        session = sa.orm.object_session(self.obj)
        # If the object has no identity and its not in session or if the object
        # has _translations relationship loaded get the locale object from the
        # relationship.
        if '_translations' not in sa.inspect(self.obj).unloaded or (
            not session or not has_identity(self.obj)
        ):
            return self.obj._translations.get(locale)

        return session.query(self.obj.__translatable__['class']).get(
            sa.inspect(self.obj).identity + (locale, )
        )

    def __getitem__(self, locale):
        if locale in self:
            locale_obj = self.fetch(locale)
            if locale_obj is not None:
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

    # Added for py2.6 compatibility
    def __length_hint__(self):
        return len(self)

    def __len__(self):
        return len(self.manager.option(self.obj, 'locales'))

    @property
    def all(self):
        return list(self.values())

    def values(self):
        for locale in self.manager.option(self.obj, 'locales'):
            yield self[locale]

    def __setitem__(self, locale, translation_obj):
        if locale in self:
            translation_obj.translation_parent = self.obj
            translation_obj.locale = locale
            self.obj._translations[locale] = translation_obj

    def __repr__(self):
        return 'TranslationsMapping(%r)' % self.obj

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
