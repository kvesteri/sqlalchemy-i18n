from .utils import option


class ImproperlyConfigured(Exception):
    pass


class UnknownLocaleError(Exception):
    def __init__(self, locale, obj):
        Exception.__init__(self,
            'Unknown locale %s given for %r. Locale is not one of %r' % (
                locale, obj, list(option(obj, 'locales'))
            )
        )
