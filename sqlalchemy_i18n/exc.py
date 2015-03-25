from .utils import option


class ImproperlyConfigured(Exception):
    pass


class UnknownLocaleError(Exception):
    def __init__(self, locale, obj):
        Exception.__init__(
            self,
            'Unknown locale %s given for instance of class %r. '
            'Locale is not one of %r' % (
                locale, obj.__class__, list(option(obj, 'locales'))
            )
        )
