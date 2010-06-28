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
"""Tests for the message string extraction tool.

$Id$
"""
import os
import doctest
import unittest
from zope.testing.doctest import DocTestSuite

class TestIsUnicodeInAllCatalog(unittest.TestCase):
    """
    """
    def setUp(self):
        pass
    
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


def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.locales.extract',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        unittest.makeSuite(TestIsUnicodeInAllCatalog),
        ))

if __name__ == '__main__':
    unittest.main()
