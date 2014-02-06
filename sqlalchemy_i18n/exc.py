from .utils import option


class ImproperlyConfigured(Exception):
    pass


class UnknownLocaleError(Exception):
    def __init__(self, locale, obj):
        Exception.__init__(self,
            'Unknown locale %s given. Locale is not one of %r' % (
                locale, list(option(obj, 'locales'))
            )
        )
