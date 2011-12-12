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


def doctest_POTMaker_add():
    """Test for POTMaker.add

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

        >>> print pm.catalog['msgid1'].comments
        #: file1.py:3
        #: file2.py:2
        <BLANKLINE>

    You can call add multiple times and it will merge the entries

        >>> pm.add({'msgid1': [('file1.zcml', 4)],
        ...         'msgid3': [('file2.zcml', 5)]})

        >>> print pm.catalog['msgid1'].comments
        #: file1.py:3
        #: file2.py:2
        #: file1.zcml:4
        <BLANKLINE>

    Unfortunately it doesn't re-sort the locations, which is arguably a bug.
    Please feel free to fix and update this test.
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
        >>> print pm.catalog['msgid1'].comments
        #: file1.py:3
        #: file2.py:2
        #: notbasedir/file3.py:5
        <BLANKLINE>

    """


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        doctest.DocTestSuite('zope.app.locales.extract',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        unittest.makeSuite(TestIsUnicodeInAllCatalog),
        unittest.makeSuite(ZCMLTest),
        ))
