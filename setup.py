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
# https://zopetoolkit.readthedocs.io/
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.app.locales package"""
import os

from setuptools import setup


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


setup(name='zope.app.locales',
      version='6.0',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.dev',
      description='Zope locale extraction and management utilities',
      long_description='\n\n'.join([
          read('README.rst'),
          'Detailed Documentation\n'
          '----------------------',
          read('src', 'zope', 'app', 'locales', 'TRANSLATE.rst'),
          read('CHANGES.rst'),
      ]),
      keywords="zope3 i18n l10n translation gettext",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Software Development :: Internationalization',
          'Framework :: Zope :: 3',
      ],
      url='https://pypi.org/project/zope.app.locales/',
      license='ZPL-2.1',
      python_requires='>=3.9',
      install_requires=[
          'setuptools',
          'zope.cachedescriptors',
          'zope.i18nmessageid >= 4.1.0',
          'zope.interface',
      ],
      extras_require=dict(
          test=[
              'zope.i18n',
              'zope.security',
              'zope.tal',
              'zope.testing',
              'zope.testrunner >= 6.4',
          ],
          zcml=[
              'zope.i18n',
              'zope.configuration',
          ],
          extract=[
              'zope.tal',
          ],
      ),
      include_package_data=True,
      zip_safe=False,
      entry_points="""
      [console_scripts]
      i18nextract=zope.app.locales.extract:main [extract]
      """)
