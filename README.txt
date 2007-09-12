This package provides some facilities for extracting and managing i18n
messages that occur in Zope software.  More specifically, i18n
messages can occur in Python code, in Page Templates and in ZCML
declarations.  ``zope.app.locales`` provides a utility that can
extract messages from all three and write them to a standard gettext
template (``pot`` file).

Changes
=======

3.4.0 (unreleased)
------------------

* Folded the i18nextract script into ``zope.app.locales.extract`` and
  exposed it as a console script entry point.

3.4.0a1 (2007-04-22)
--------------------

Initial release as a separate project, corresponds to zope.app.locales
from Zope 3.4.0a1

