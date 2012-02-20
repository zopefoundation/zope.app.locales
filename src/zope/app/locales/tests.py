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
__docformat__ = 'restructuredtext'

import doctest
import os
import unittest
import zope.app.locales
import zope.component
import zope.configuration.xmlconfig


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
                        mcatalog = GettextMessageCatalog(lang, 'zope',
                                           os.path.join(lc_path, f))
                        catalog = mcatalog._catalog
                        self.failUnless(catalog._charset,
            u"""Charset value for the Message catalog is missing.
                The language is %s (zope.po).
                Value of the message catalog should be in unicode""" % (lang,)
                                        )


class ZCMLTest(unittest.TestCase):

    def test_configure_zcml_should_be_loadable(self):
        try:
            zope.configuration.xmlconfig.XMLConfig(
                'configure.zcml', zope.app.locales)()
        except Exception, e:
            self.fail(e)

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
        [('file1.py', 3), ('file2.py', 2)]

    You can call add multiple times and it will merge the entries

        >>> pm.add({'msgid1': [('file1.zcml', 4)],
        ...         'msgid3': [('file2.zcml', 5)]})

        >>> pm.catalog['msgid1'].locations
        [('file1.py', 3), ('file1.zcml', 4), ('file2.py', 2)]

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
        [('file1.py', 3), ('file2.py', 2), ('notbasedir/file3.py', 5)]

    """


def doctest_POTMaker_write():
    r"""Test for POTMaker.write

        >>> from zope.app.locales.extract import POTMaker
        >>> path = 'test.pot'
        >>> pm = POTMaker(path, '')
        >>> pm.add({'msgid1': [('file2.py', 2), ('file1.py', 3)],
        ...         'msgid2': [('file1.py', 5)]})
        >>> from zope.app.locales.pygettext import make_escapes
        >>> make_escapes(0)
        >>> pm.write()

        >>> f = open(path)
        >>> pot = f.read()
        >>> print pot
        ##############################################################################
        #
        # Copyright (c) 2003-2004 Zope Foundation and Contributors.
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
        "Project-Id-Version: Meaningless\n"
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

        >>> f.close()
        >>> os.remove(path)

    """


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(
            optionflags=doctest.NORMALIZE_WHITESPACE|
                        doctest.ELLIPSIS|
                        doctest.REPORT_NDIFF,),
        doctest.DocTestSuite('zope.app.locales.extract',
            optionflags=doctest.NORMALIZE_WHITESPACE|
                        doctest.ELLIPSIS|
                        doctest.REPORT_NDIFF,),
        unittest.makeSuite(TestIsUnicodeInAllCatalog),
        unittest.makeSuite(ZCMLTest),
        ))
