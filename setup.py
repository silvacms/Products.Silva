# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '3.0.4'

tests_require = [
    'silva.pas.base',
    'infrae.testing',
    'infrae.testbrowser',
    'infrae.wsgi [test]',
    ]

def product_readme(filename):
    return open(os.path.join("Products", "Silva", filename)).read()


setup(name='Products.Silva',
      version=version,
      description="Silva Content Management System",
      long_description=product_readme("README.txt") + "\n" +
                       product_readme("HISTORY.txt"),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva cms zope',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/Products.Silva',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'PIL',
        'Products.SilvaMetadata',
        'Sprout',
        'ZODB3 >= 3.9',
        'Zope2',
        'five.grok',
        'five.localsitemanager',
        'grokcore.chameleon',
        'infrae.comethods',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.layout',
        'silva.core.messages',
        'silva.core.references',
        'silva.core.services',
        'silva.core.smi',
        'silva.core.upgrade',
        'silva.core.views',
        'silva.core.xml',
        'silva.translations',
        'silva.ui',
        'silvatheme.standardissue',
        'zeam.form.silva',
        'zope.annotation',
        'zope.app.schema',
        'zope.container',
        'zope.component',
        'zope.container',
        'zope.contenttype',
        'zope.event',
        'zope.i18n',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.site',
        'zope.traversing',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
