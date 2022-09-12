================
zope.app.locales
================

This package provides some facilities for extracting and managing i18n
messages that occur in Zope software.  More specifically, i18n
messages can occur in Python code, in Page Templates and in ZCML
declarations.  ``zope.app.locales`` provides a utility that can
extract messages from all three and write them to a standard gettext
template (``pot`` file).

Usage
-----

Version 4.2 does not contain any ``*.mo`` files. They are the compiled
translation files (``*.po``). (Future versions will contain them again.)

To generate or update ``*.mo`` files on the fly set the following environment
variable::

    zope_i18n_compile_mo_files=True

To restrict the allowed languages set ``zope_i18n_allowed_languages`` to a list
of languages. Example::

    zope_i18n_allowed_languages=de,en,es,fr
