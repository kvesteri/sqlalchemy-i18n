Changelog
---------

Here you can see the full list of changes between each SQLAlchemy-i18n release.


1.0.3 (2017-01-30)
^^^^^^^^^^^^^^^^^^

- Set autoincrement as False for translation class inherited primary keys


1.0.2 (2016-03-06)
^^^^^^^^^^^^^^^^^^

- Added ``translations_relationship_args`` configuration option
- Added ``foreign_key_args`` parameter to ``translations_base`` function


1.0.1 (2014-10-21)
^^^^^^^^^^^^^^^^^^

- Made current_locale expression a GenericFunction


1.0 (2014-10-21)
^^^^^^^^^^^^^^^^

- Made current_translation work with same schematics as class variable and object variable.
- Added get_fallback_locale utility function
- Added fallback_translation hybrid property


0.9.0 (2014-09-30)
^^^^^^^^^^^^^^^^^^

- Added support for classical SQLAlchemy mappings


0.8.4 (2014-04-21)
^^^^^^^^^^^^^^^^^^

- Added enhanced column aliases handling
- Updated SQLAlchemy-Utils dependency to 0.25.3


0.8.3 (2014-02-15)
^^^^^^^^^^^^^^^^^^

- Fixed infinite recursion issue with UnknownLocaleError when given object repr() uses
translated columns


0.8.2 (2014-02-07)
^^^^^^^^^^^^^^^^^^

- Add custom base class support for translation_base
- Better exception message for UnknownLocaleError


0.8.1 (2014-02-07)
^^^^^^^^^^^^^^^^^^

- Fixed common base class handling (__translatable__ args copied to each child class now)


0.8.0 (2014-02-06)
^^^^^^^^^^^^^^^^^^

- Add _translations relationship for translatable classes
- Rewritten relationship model for translatable classes
- New more robust syntax for declaring translation models
- Composite primary key support for translation parent classes


0.7.1 (2013-10-10)
^^^^^^^^^^^^^^^^^^

- Added default_locale utility function


0.7.0 (2013-10-10)
^^^^^^^^^^^^^^^^^^

- Translatable.translations now a hybrid property instead of regular property (allows flexible querying)
- New utility function find_translations


0.6.13 (2013-10-07)
^^^^^^^^^^^^^^^^^^^

- Fixed hybrid property collision detection for single table inheritance


0.6.12 (2013-10-07)
^^^^^^^^^^^^^^^^^^^

- Added property collision detection for generated hybrid properties
- Added hybrid property exclusion for hybrid property generator


0.6.11 (2013-10-07)
^^^^^^^^^^^^^^^^^^^

- Hybrid property builder now checks for manager options if class option 'default_locale' is not set.


0.6.10 (2013-09-16)
^^^^^^^^^^^^^^^^^^^

- Support for callables as default locales


0.6.9 (2013-09-13)
^^^^^^^^^^^^^^^^^^

- Fixed object to string conversion in current_translation methods


0.6.8 (2013-09-11)
^^^^^^^^^^^^^^^^^^

- Fixed fatal bug in set_not_nullables_to_empty_strings which would cause setting of already assigned translation columns to empty strings


0.6.7 (2013-09-11)
^^^^^^^^^^^^^^^^^^

- Listener set_not_nullables_to_empty_strings invoked even if locale object already exists


0.6.6 (2013-09-10)
^^^^^^^^^^^^^^^^^^

- Translation auto generation with nullable to empty string auto setting now works with join table inheritance


0.6.5 (2013-09-10)
^^^^^^^^^^^^^^^^^^

- Translation auto creation now sets not nullable translated columns without defaults as empty strings


0.6.4 (2013-09-10)
^^^^^^^^^^^^^^^^^^

- Translation hybrid properties now fallback to default locale for empty strings


0.6.3 (2013-08-15)
^^^^^^^^^^^^^^^^^^

- Added get_locale_fallback option


0.6.2 (2013-08-13)
^^^^^^^^^^^^^^^^^^

- Fixed translation auto-creation


0.6.1 (2013-08-13)
^^^^^^^^^^^^^^^^^^

- Added unified and easily overridable global configuration


0.6.0 (2013-08-09)
^^^^^^^^^^^^^^^^^^

- Completely rewritten translation relationships


0.5.1 (2013-06-26)
^^^^^^^^^^^^^^^^^^

- Translation auto creation listener added


0.5.0 (2013-06-25)
^^^^^^^^^^^^^^^^^^

- Added TranslationManager


0.4.1 (2013-06-11)
^^^^^^^^^^^^^^^^^^

- Base classes option no longer mandatory


0.4.0 (2013-06-10)
^^^^^^^^^^^^^^^^^^

- New, more extendable syntax for setting up translatable models (make_translatable utility function)


0.3.2 (2013-06-05)
^^^^^^^^^^^^^^^^^^

- Fixed current_translation proxy window building


0.3.1 (2013-06-04)
^^^^^^^^^^^^^^^^^^

- Updated SQLAlchemy-Utils requirements to 0.12.4


0.3.0 (2013-05-30)
^^^^^^^^^^^^^^^^^^

- Added force_locale
- Rewrote current_translation schematics


0.2.4 (2013-05-29)
^^^^^^^^^^^^^^^^^^

- Updated SQLAlchemy-Utils requirements to 0.12.2


0.2.3 (2013-05-20)
^^^^^^^^^^^^^^^^^^

- Renamed __locale_getter__ to get_locale


0.2.2 (2013-05-20)
^^^^^^^^^^^^^^^^^^

- Made __locale_getter__ a class attribute for more robust overriding


0.2.1 (2013-05-19)
^^^^^^^^^^^^^^^^^^

- Added hybrid_property expressions for current_translation and translations


0.2.0 (2013-05-17)
^^^^^^^^^^^^^^^^^^

- ProxyDict moved to SQLAlchemy-Utils
- SQLAlchemy-Utils added as dependency
- Completely rewritten inheritance handling


0.1.5 (2013-05-16)
^^^^^^^^^^^^^^^^^^

- Column locale defined right after primary keys


0.1.4 (2013-05-16)
^^^^^^^^^^^^^^^^^^

- Fixed translatable options handling when using common base class


0.1.3 (2013-05-16)
^^^^^^^^^^^^^^^^^^

- Joined table inheritance support


0.1.2 (2013-05-15)
^^^^^^^^^^^^^^^^^^

- Added base_classes configuration option


0.1.1 (2013-05-15)
^^^^^^^^^^^^^^^^^^

- Generated translations class names now in format '[ParentClass]Translation'


0.1.0 (2013-05-13)
^^^^^^^^^^^^^^^^^^

- Initial release
