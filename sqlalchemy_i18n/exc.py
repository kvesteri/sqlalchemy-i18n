from .utils import option


class UnknownLocaleError(Exception):
    def __init__(self, locale, obj):
        self.message = 'Unknown locale %s given. Locale is not one of %r' % (
            locale, list(option(obj, 'locales'))
        )
