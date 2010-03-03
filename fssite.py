# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import zope.deferredimport

zope.deferredimport.deprecated(
    'Please import directly from Products.FileSystemSite.DirectoryView '
    'this import will be removed in Silva 2.3',
    registerDirectory='Products.FileSystemSite.DirectoryView:registerDirectory',
    registerFileExtension='Products.FileSystemSite.DirectoryView:registerFileExtension',
    manage_addDirectoryView='Products.FileSystemSite.DirectoryView:manage_addDirectoryView')

zope.deferredimport.deprecated(
    'Please import directly from Products.FileSystemSite.FSImage '
    'this import will be removed in Silva 2.3',
    FSImage='Products.FileSystemSite.FSImage:FSImage')

zope.deferredimport.deprecated(
    'Please import directly from Products.FileSystemSite.FSDTMLMethod '
    'this import will be removed in Silva 2.3',
    FSDTMLMethod='Products.FileSystemSite.FSDTMLMethod:FSDTMLMethod')

zope.deferredimport.deprecated(
    'Please import directly from Products.FileSystemSite.FSPageTemplate '
    'this import will be removed in Silva 2.3',
    FSPageTemplate='Products.FileSystemSite.FSPageTemplate:FSPageTemplate')

zope.deferredimport.deprecated(
    'Please import directly from Products.FileSystemSite.utils '
    'this import will be removed in Silva 2.3',
    minimalpath='Products.FileSystemSite.utils:minimalpath',
    expandpath='Products.FileSystemSite.utils:expandpath')


