Installation
============

This part of the documentation covers the installation of SQLAlchemy-i18n.

Supported platforms
-------------------

SQLAlchemy-i18n has been tested against the following Python platforms.

- cPython 2.6
- cPython 2.7
- cPython 3.3
- cPython 3.4
- cPython 3.5


Installing an official release
------------------------------

You can install the most recent official SQLAlchemy-i18n version using
pip_::

    pip install sqlalchemy-i18n

.. _pip: http://www.pip-installer.org/

Installing the development version
----------------------------------

To install the latest version of SQLAlchemy-i18n, you need first obtain a
copy of the source. You can do that by cloning the git_ repository::

    git clone git://github.com/kvesteri/sqlalchemy-i18n.git

Then you can install the source distribution using the ``setup.py``
script::

    cd sqlalchemy-i18n
    python setup.py install

.. _git: http://git-scm.org/

Checking the installation
-------------------------

To check that SQLAlchemy-i18n has been properly installed, type ``python``
from your shell. Then at the Python prompt, try to import SQLAlchemy-i18n,
and check the installed version:

.. parsed-literal::

    >>> import sqlalchemy_i18n
    >>> sqlalchemy_i18n.__version__
    |release|
