##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.app.locales package

$Id$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.locales',
      version='3.7.4',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope locale extraction and management utilities',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '----------------------\n'
          + '\n\n' +
          read('src', 'zope', 'app', 'locales', 'TRANSLATE.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 i18n l10n translation gettext",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Software Development :: Internationalization',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/zope.app.locales',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      install_requires=['setuptools',
                        'zope.i18nmessageid',
                        'zope.interface',
                        ],
      extras_require = dict(
          test=[
              'zope.i18n',
              'zope.tal',
              'zope.testing',
                ],
          zcml=[
              'zope.i18n',
              'zope.configuration',
              ],
          extract=[
              'zope.tal',
              'zope.app.applicationcontrol',
              'zope.app.appsetup',
              ],
          ),
      include_package_data = True,
      zip_safe = False,
      entry_points="""
      [console_scripts]
      i18nextract = zope.app.locales.extract:main [extract]
      """
      )
