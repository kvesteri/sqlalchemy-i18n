Changelog
---------

Here you can see the full list of changes between each SQLAlchemy-i18n release.


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
