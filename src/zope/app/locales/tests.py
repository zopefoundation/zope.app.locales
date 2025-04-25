##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests for the message string extraction tool."""
import contextlib
import doctest
import os
import re
import shutil
import sys
import tempfile
import unittest

import zope.component
import zope.configuration.xmlconfig
from zope.testing import renormalizing

import zope.app.locales
import zope.app.locales.extract


class TestIsUnicodeInAllCatalog(unittest.TestCase):

    def test_is_unicode(self):
        from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
        path = os.path.dirname(__file__)
        langs = os.listdir(path)
        for lang in langs:
            lc_path = os.path.join(path, lang, 'LC_MESSAGES')
            if os.path.isdir(lc_path):
                files = os.listdir(lc_path)
                for f in files:
                    if f.endswith('.mo'):
                        mcatalog = GettextMessageCatalog(
                            lang, 'zope', os.path.join(lc_path, f))
                        catalog = mcatalog._catalog
                        self.assertTrue(
                            catalog._charset,
                            "Charset value for the Message catalog is"
                            " missing. The language is %s (zope.po). Value of"
                            " the message catalog should be in unicode""" % (
                                lang,))


class ZCMLTest(unittest.TestCase):

    def test_configure_zcml_should_be_loadable(self):
        zope.configuration.xmlconfig.XMLConfig(
            'configure.zcml', zope.app.locales)()

    def test_configure_should_register_n_components(self):
        gsm = zope.component.getGlobalSiteManager()
        u_count = len(list(gsm.registeredUtilities()))
        a_count = len(list(gsm.registeredAdapters()))
        s_count = len(list(gsm.registeredSubscriptionAdapters()))
        h_count = len(list(gsm.registeredHandlers()))
        zope.configuration.xmlconfig.XMLConfig(
            'configure.zcml', zope.app.locales)()
        self.assertEqual(u_count + 2, len(list(gsm.registeredUtilities())))
        self.assertEqual(a_count, len(list(gsm.registeredAdapters())))
        self.assertEqual(
            s_count, len(list(gsm.registeredSubscriptionAdapters())))
        self.assertEqual(h_count, len(list(gsm.registeredHandlers())))

    def test_zcml_extraction(self):
        zcml = """
            <configure xmlns="http://namespaces.zope.org/zope"
                       i18n_domain="testdomain">
              <include package="zope.security" file="meta.zcml" />
                <permission
                  id="testpkg.TestPermission"
                  title="Test Permission"
                  description="This test permission is defined in ZCML"
                />
            </configure>
        """
        dirname = tempfile.mkdtemp(prefix='zope-app-locales-tests-')
        self.addCleanup(shutil.rmtree, dirname)

        fn = os.path.join(dirname, 'configure.zcml')
        with open(fn, 'w') as zcmlfile:
            zcmlfile.write(zcml)

        # basepath is removed if in sys.path:
        try:
            sys.path.append(dirname)
            strings = zope.app.locales.extract.zcml_strings(
                'unused', 'testdomain', site_zcml=fn)
        finally:
            sys.path.remove(dirname)
        self.assertEqual(
            sorted(strings.items()),
            [('Test Permission',
              [('configure.zcml', 5)]),
             ('This test permission is defined in ZCML',
              [('configure.zcml', 5)])])
        # If basepath is not in sys.path it is kept, only the leading '/' is
        # removed:
        strings = zope.app.locales.extract.zcml_strings(
            'unused', 'testdomain', site_zcml=fn)
        example_path = strings['Test Permission'][0][0]
        self.assertTrue(
            example_path.startswith(dirname[1:]),
            f'{example_path!r} does not start with {dirname[1:]!r}')


def doctest_POTEntry_sort_order():
    """Test for POTEntry.__cmp__

        >>> from zope.app.locales.extract import POTEntry

    'file1' comes before 'file2'

        >>> pe1 = POTEntry('msgid1')
        >>> pe1.addLocationComment('file1', 42)

        >>> pe2 = POTEntry('msgid1')
        >>> pe2.addLocationComment('file2', 42)

        >>> pe1 < pe2
        True

    line 9 comes before line 42

        >>> pe3 = POTEntry('msgid1')
        >>> pe3.addLocationComment('file1', 9)

        >>> pe3 < pe1
        True

    Finally, msgid1 comes before msgid2

        >>> pe4 = POTEntry('msgid2')
        >>> pe4.addLocationComment('file1', 42)

        >>> pe1 < pe4
        True

    """


def doctest_POTMaker_add():
    r"""Test for POTMaker.add

        >>> from zope.app.locales.extract import POTMaker
        >>> pm = POTMaker('/dev/null', 'path')
        >>> pm.add({'msgid1': [('file2.py', 2), ('file1.py', 3)],
        ...         'msgid2': [('file1.py', 5)]})

        >>> sorted(pm.catalog)
        ['msgid1', 'msgid2']

        >>> pm.catalog['msgid1']
        <POTEntry: 'msgid1'>

        >>> pm.catalog['msgid2']
        <POTEntry: 'msgid2'>

    The locations have been sorted

        >>> pm.catalog['msgid1'].locations
        (('file1.py', 3), ('file2.py', 2))

    You can call add multiple times and it will merge the entries

        >>> pm.add({'msgid1': [('file1.zcml', 4)],
        ...         'msgid3': [('file2.zcml', 5)]})

        >>> pm.catalog['msgid1'].locations
        (('file1.py', 3), ('file1.zcml', 4), ('file2.py', 2))

    """


def doctest_POTMaker_add_skips_blank_msgids():
    """Test for POTMaker.add

        >>> from zope.app.locales.extract import POTMaker
        >>> pm = POTMaker('/dev/null', 'path')
        >>> pm.add({'': [('file2.py', 2), ('file1.py', 3)]})
        >>> sorted(pm.catalog)
        []

    """


def doctest_POTMaker_add_strips_basedirs():
    """Test for POTMaker.add

        >>> from zope.app.locales.extract import POTMaker
        >>> pm = POTMaker('/dev/null', 'path')
        >>> pm.add({'msgid1': [('basedir/file2.py', 2),
        ...                    ('file1.py', 3),
        ...                    ('notbasedir/file3.py', 5)]},
        ...        'basedir/')
        >>> pm.catalog['msgid1'].locations
        (('file1.py', 3), ('file2.py', 2), ('notbasedir/file3.py', 5))

    """


def doctest_POTMaker_write():
    r"""Test for POTMaker.write

        >>> from zope.app.locales.extract import POTMaker
        >>> tmpdir = tempfile.mkdtemp(prefix='zope.app.locales-test-')
        >>> path = os.path.join(tmpdir, 'test.pot')
        >>> pm = POTMaker(path, '')
        >>> pm.add({'msgid1': [('file2.py', 2), ('file1.py', 3)],
        ...         'msgid2': [('file1.py', 5)]})
        >>> from zope.app.locales.pygettext import make_escapes
        >>> make_escapes(0)
        >>> pm.write()

        >>> with open(path) as f:
        ...     pot = f.read()
        ...     print(pot)
        ##############################################################################
        #
        # Copyright (c) 2003-2019 Zope Foundation and Contributors.
        # All Rights Reserved.
        #
        # This software is subject to the provisions of the Zope Public License,
        # Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
        # THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
        # WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
        # WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
        # FOR A PARTICULAR PURPOSE.
        #
        ##############################################################################
        msgid ""
        msgstr ""
        "Project-Id-Version: Unknown\n"
        "POT-Creation-Date: ...\n"
        "PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
        "Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
        "Language-Team: Zope 3 Developers <zope-dev@zope.org>\n"
        "MIME-Version: 1.0\n"
        "Content-Type: text/plain; charset=UTF-8\n"
        "Content-Transfer-Encoding: 8bit\n"
        "Generated-By: zope/app/locales/extract.py\n"
        <BLANKLINE>
        #: file1.py:3
        #: file2.py:2
        msgid "msgid1"
        msgstr ""
        <BLANKLINE>
        #: file1.py:5
        msgid "msgid2"
        msgstr ""
        <BLANKLINE>
        <BLANKLINE>

        >>> shutil.rmtree(tmpdir)

    """  # noqa: E501


def doctest_POTMaker_custom_header():
    r"""Test for POTMaker.write

        >>> from zope.app.locales.extract import POTMaker
        >>> tmpdir = tempfile.mkdtemp(prefix='zope.app.locales-test-')
        >>> path = os.path.join(tmpdir, 'test.pot')
        >>> header_template = os.path.join(
        ...     os.path.dirname(__file__), 'fixtures', 'header_template.txt')
        >>> pm = POTMaker(path, '', header_template)
        >>> pm.add({'msgid2': [('file1.py', 5)]})
        >>> from zope.app.locales.pygettext import make_escapes
        >>> make_escapes(0)
        >>> pm.write()

        >>> with open(path) as f:
        ...     pot = f.read()
        ...     print(pot)
        # (probably too) minimal example header template
        "Project-Id-Version: Unknown\\n"
        "POT-Creation-Date: ...\n"
        "Content-Type: text/plain; charset=UTF-8\\n"
        "Content-Transfer-Encoding: 8bit\\n"
        <BLANKLINE>
        #: file1.py:5
        msgid "msgid2"
        msgstr ""
        <BLANKLINE>
        <BLANKLINE>
        >>> shutil.rmtree(tmpdir)

    """


def doctest_POTMaker_custom_header_not_existing_file():
    r"""Test for POTMaker.write

        >>> from zope.app.locales.extract import POTMaker
        >>> POTMaker('test.pot', '', 'header_template.txt')
        Traceback (most recent call last):
        ValueError: Path '/.../zope.app.locales/header_template.txt' derived from 'header_template.txt' does not exist.

    """  # noqa: E501


class MainTestMixin:

    main = None

    @contextlib.contextmanager
    def patched_sys(self, exit_code=None):
        import sys
        from io import StringIO

        _exit = sys.exit
        stderr = sys.stderr
        stdout = sys.stdout
        try:
            def sys_exit(code):
                self.assertEqual(exit_code, code)
                raise SystemExit()
            sys.exit = sys_exit
            err = sys.stderr = StringIO()
            out = sys.stdout = StringIO()
            if exit_code is not None:
                with self.assertRaises(SystemExit):
                    yield out, err
            else:
                yield out, err
        finally:
            sys.exit = _exit
            sys.stderr = stderr
            sys.stdout = stdout

    def run_patched(self, argv, exit_code=None):
        with self.patched_sys(exit_code) as (out, err):
            self.main(argv)
        return out, err

    def test_main_help(self):
        self.run_patched(['-h'], 0)


class TestExtract(MainTestMixin,
                  unittest.TestCase):

    def main(self, argv):
        from zope.app.locales.extract import main
        main(argv)

    def test_main_extract(self):
        _out, err = self.run_patched([], 1)
        self.assertIn("the module search path", err.getvalue())

        _out, err = self.run_patched(['-p', os.path.dirname(__file__)], 1)
        self.assertIn('location of the root ZCML file', err.getvalue())

        _out, err = self.run_patched(['-p', os.path.dirname(__file__),
                                      '-s', 'no such file'], 1)
        self.assertIn('does not exist', err.getvalue())

        temp = tempfile.mkdtemp(prefix='zope-app-locales-tests-')
        self.addCleanup(shutil.rmtree, temp)

        # An object that can look like the usual i18n
        # marker, but we'll do different things with it for coverage
        # to be sure they're handled
        class X:
            def __add__(self, other):
                return self

        _ = X()
        _ = _ + _

        out, err = self.run_patched([
            '-p', os.path.dirname(__file__),
            '-s', os.path.join(os.path.dirname(__file__), 'configure.zcml'),
            '-o', temp],
        )
        self.assertIn('base path:', out.getvalue())

        with open(os.path.join(temp, 'zope.pot')) as f:
            pot_data = f.read()

        self.assertIn('Project-Id-Version: Unknown', pot_data)

    def test_py_strings_verify_domain(self):
        from zope.app.locales.extract import _import_chickens
        from zope.app.locales.extract import py_strings

        cat = py_strings(os.path.dirname(__file__), verify_domain=True)
        self.assertEqual({}, cat)

        # Now with a fake MessageFactory with no domain
        tests = __import__('tests', *_import_chickens)
        assert not hasattr(tests, '_')

        class MessageFactory:
            pass

        try:
            tests._ = MessageFactory
            with self.patched_sys() as (_out, err):
                cat = py_strings(os.path.dirname(__file__), verify_domain=True)
            self.assertEqual({}, cat)
            self.assertIn(
                "Could not figure out the i18n domain", err.getvalue())

            # Now with the wrong domain
            MessageFactory._domain = 'notthedomain'
            with self.patched_sys() as (out, err):
                cat = py_strings(os.path.dirname(__file__), verify_domain=True)
            self.assertEqual({}, cat)
            self.assertEqual('', out.getvalue())
            self.assertEqual('', err.getvalue())
        finally:
            del tests._


class TestPygettext(MainTestMixin,
                    unittest.TestCase):

    def main(self, argv):
        from zope.app.locales.pygettext import main
        main(argv)

    def test_extract(self):
        me = __file__
        if me.endswith((".pyc", ".pyo")):
            me = me[:-1]
        out, _err = self.run_patched(['-d', 'TESTDOMAIN',
                                      '-v', '-a', '-D', '-o', '-', me])
        self.assertIn('POT-Creation-Date', out.getvalue())


checker = renormalizing.RENormalizing([
    (re.compile(r"b'([^']*)'"), r"'\1'"),
    (re.compile(r"u'([^']*)'"), r"'\1'"),
])


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(
            optionflags=(doctest.NORMALIZE_WHITESPACE
                         | doctest.ELLIPSIS
                         | doctest.REPORT_NDIFF),
            checker=checker),
        doctest.DocTestSuite(
            'zope.app.locales.extract',
            optionflags=(doctest.NORMALIZE_WHITESPACE
                         | doctest.ELLIPSIS
                         | doctest.REPORT_NDIFF),
            checker=checker),
        unittest.defaultTestLoader.loadTestsFromName(__name__),
    ))
