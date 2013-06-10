from contextlib import contextmanager
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import proxy_dict


class Translatable(object):
    __translatable__ = {
        'default_locale': 'en'
    }
    __pending_translatables__ = []
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
        return self._forced_locale or self.get_locale()

    @hybrid_property
    def current_translation(self):
        locale = str(self._get_locale())
        self.init_translation_proxy_window(locale)

        if locale in self.translations:
            locale_obj = getattr(self, '_translation_%s' % locale)
            if locale_obj != self.translations[locale]:
                setattr(
                    self,
                    '_translation_%s' % locale,
                    self.translations[locale]
                )
            return self.translations[locale]

        class_ = self.__translatable__['class']
        obj = class_()
        obj.locale = locale
        self.translations[locale] = obj
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
        try:
            return getattr(cls, '_translation_%s' % locale)
        except AttributeError:
            cls.init_translation_proxy_window(locale)
            return getattr(cls, '_translation_%s' % locale)

    @classmethod
    def init_translation_proxy_window(cls, locale):
        translation_cls = cls.__translatable__['class']
        if not hasattr(cls, '_translation_%s' % locale):
            setattr(
                cls,
                '_translation_%s' % locale,
                sa.orm.relationship(
                    translation_cls,
                    primaryjoin=sa.and_(
                        cls.id == translation_cls.id,
                        translation_cls.locale == locale
                    ),
                    foreign_keys=[cls.id],
                    uselist=False,
                    viewonly=True
                )
            )

    @hybrid_property
    def translations(self):
        return proxy_dict(
            self,
            '_translations',
            getattr(self.__translatable__['class'], 'locale')
        )

    @translations.expression
    def translations(cls):
        return cls._translations

    @classmethod
    def __declare_last__(cls):
        if not cls.__translatable__.get('class'):
            cls.__pending_translatables__.append(cls)
