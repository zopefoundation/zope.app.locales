##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
import doctest
import unittest
from zope.testing.doctest import DocTestSuite

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.locales.extract',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        ))

if __name__ == '__main__':
    unittest.main()