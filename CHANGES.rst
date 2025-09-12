=======
CHANGES
=======

6.0 (2025-09-12)
----------------

- Replace ``pkg_resources`` namespace with PEP 420 native namespace.


5.1 (2025-08-08)
----------------

- Add support for Python 3.12, 3.13.

- Drop support for Python 3.7, 3.8.

- Fix one pt_BR translation.
  (`#21 <https://github.com/zopefoundation/zope.app.locales/pull/21>`_)


5.0 (2023-08-28)
----------------

- Add support for Python 3.11.

- Drop support for Python 2.7, 3.5, 3.6.


4.3 (2022-09-12)
----------------

- Remove ``*.mo`` files from the repository and document in the README how to
  generate them on the fly.
  (`#7 <https://github.com/zopefoundation/zope.app.locales/issues/7>`_)

- Automatically create ``*.mo`` files during the release process so this
  release will again contain ``*.mo`` files.

4.2 (2022-06-10)
----------------

- Add support for Python 3.9, 3.10.

- Make path in ZCML extraction relative.

- This release does not contain any ``*.mo`` files.


4.1 (2019-06-24)
----------------

- Flake8 the code.

- Add support for Python 3.7, 3.8b1 and PyPy3.

- Port usage of custom POT file header template here from `z3c.recipe.i18n`.
  (`#11 <https://github.com/zopefoundation/zope.app.locales/pull/11>`_)

- Prevent POT files from collecting duplicate location specifiers over time.
  (`#12 <https://github.com/zopefoundation/zope.app.locales/pull/12>`_)


4.0.1 (2018-06-29)
------------------

- Recompile the `*.mo` translation files.


4.0.0 (2017-05-02)
------------------

- Add support for Python 3.5 and 3.6 and PyPy.


3.7.5 (2016-03-28)
------------------

- Add a test for the zcml_extraction.

- Remove zope.app.applicationcontrol and zope.app.appsetup dependencies.

- Add list of supported Python versions to Trove classifiers.


3.7.4 (2012-05-14)
------------------

- In version 3.7.2 msgids and default values were forced to be
  ``unicode``. This was too strict because at least the TAL extractor returns
  UTF-8 encoded default values. Fixed this by allowing the default value to
  be a string again.


3.7.3 (2012-01-06)
------------------

- i18nextract bugfix: _("msgid", mapping={...}) does not have a default, just
  like _("msgid").  Previously it would get a ``#. Default: ""`` annotation in
  the .pot file.


3.7.2 (2011-12-12)
------------------

- Handle Unicode msgids and default values.

- Consistent sorting of source filenames for each msgid.  Also sort line
  numbers numerically, not lexicographically.


3.7.1 (2011-12-07)
------------------

- Fix nl translations.

- Updated Brazilian Portuguese translation [erico_andrei]

3.7.0 (2011-03-02)
------------------

- Include zcml dependencies in ``configure.zcml``, require the necessary
  packages via a `zcml` extra, added tests for zcml.

- Using Python's ``doctest`` module instead of depreacted
  ``zope.testing.doctest``.


3.6.2 (2010-07-31)
------------------

- Updated copyright to `Zope Foundation`, even in pot template.

- Updated e-mail address in pot template to current address of zope
  mailing list.

- Added missing test dependency on `zope.i18n`.


3.6.1 (2010-05-17)
------------------

- Updated Dutch and German translations.

3.6.0 (2009-12-28)
------------------

- Added `configure.zcml` which registers the translations in the
  package. So the package contains its configuration. (Till now it was
  done in `zope.app.zcmlfiles`.)

3.5.2 (2009-12-22)
------------------

- Updated tests to handle Unicode correctly.

- Update Japanese Translation (thanks Takeshi Yamamoto).

3.5.1 (2009-01-27)
------------------

* Added missing dependency (zope.tal) for tests.

3.5.0 (2009-01-26)
------------------

* Moved the dependencies of the extract console script into an `extract`
  extras_require to avoid runtime dependencies.

* Fixed bug #227582 (bad size in zh_CN locale)

3.4.5 (2008-07-16)
------------------

* added filePattern parameter for tal_strings to be able to not only parse
  `.pt` files.

* Updated Dutch translation

3.4.4 (2008-03-05)
------------------

* Updated Spanish translation

3.4.3 (2008-02-20)
------------------

* Updated Spanish translation

* Updated Japanese translation

3.4.2 (2008-02-06)
------------------

* Fixed and updated Russian translation. Fixed issue #186628 (Typos and errors
  in russian translation)

3.4.1 (2007-12-12)
------------------

* Fixed and updated the french translation

3.4.0 (2007-10-25)
------------------

* Folded the i18nextract script into ``zope.app.locales.extract`` and
  exposed it as a console script entry point.

3.4.0a1 (2007-04-22)
--------------------

* Initial release as a separate project, corresponds to ``zope.app.locales``
  from Zope 3.4.0a1
