# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '2.2.1'

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
      url='http://infrae.com/products/silva',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      tests_require=[
        'silva.export.opendocument',
        ],
      install_requires=[
        'PILwoTK',
        'GenericCache',
        'Products.SilvaDocument',
        'Products.SilvaFind',
        'Products.SilvaLayout',
        'Products.SilvaKupu',
        'Products.SilvaMetadata',
        'Products.SilvaViews',
        'Products.Formulator',
        'Products.FileSystemSite',
        'Products.Groups',
        'Products.ParsedXML',
        'Products.XMLWidgets',
        'Sprout',
        'five.grok',
        'five.localsitemanager',
        'lxml >= 2.1.1',
        'setuptools',
        'silva.core.conf',
        'silva.core.views',
        'silva.core.layout',
        'silva.core.smi',
        'silva.core.services',
        'silva.core.interfaces',
        'silva.core.upgrade',
        'silva.translations',
        'zope.contenttype',
        'silvatheme.standardissue',
        ],
      )
