from contextlib import contextmanager
from sqlalchemy.ext.hybrid import hybrid_property


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
        old_forced_locale = self._forced_locale
        self._forced_locale = locale
        yield
        self._forced_locale = old_forced_locale

    def _get_locale(self):
        locale = self._forced_locale or self.get_locale()
        if locale:
            return locale

        manager = self.__translatable__['manager']
        if manager.option(self, 'get_locale_fallback'):
            return manager.option(self, 'default_locale')

    @hybrid_property
    def current_translation(self):
        locale = str(self._get_locale())
        locale_obj = getattr(self, '_translation_%s' % locale)
        if locale_obj:
            return locale_obj

        class_ = self.__translatable__['class']

        obj = class_(translation_parent=self)

        obj.locale = locale
        setattr(
            self,
            '_translation_%s' % locale,
            obj
        )
        return obj

    @current_translation.setter
    def current_translation(self, obj):
        locale = str(self._get_locale())
        obj.locale = locale
        self.translations[locale] = obj

    @current_translation.expression
    def current_translation(cls):
        locale = str(cls.get_locale.im_func(cls))
        return getattr(cls, '_translation_%s' % locale)

    @property
    def translations(self):
        return TranslationsMapping(self)


class TranslationsMapping(object):
    def __init__(self, obj):
        self.obj = obj
        self.manager = self.obj.__translatable__['manager']

    def __contains__(self, locale):
        return locale in self.manager.option(self.obj, 'locales')

    def format_key(self, locale):
        return  '_translation_%s' % locale

    def __getitem__(self, locale):
        if locale in self:
            return getattr(self.obj, self.format_key(locale))

    def __setitem__(self, locale, obj):
        if locale in self:

            setattr(self.obj, self.format_key(locale), obj)

    def items(self):
        data = []
        for locale in self.manager.option(self.obj, 'locales'):
            data.append((locale, self[locale]))
        return data

    def iteritems(self):
        for locale in self.manager.option(self.obj, 'locales'):
            yield locale, self[locale]
