# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core.interfaces import IFolder, IPublication
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer


class FolderConvertionTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_folder_to_publication(self):
        """Test Silva Folder to Silva Publication conversion.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')
        self.assertTrue('folder' in self.root.objectIds('Silva Folder'))
        self.assertTrue(verifyObject(IFolder, self.root.folder))

        self.root.folder.to_publication()

        self.assertFalse('folder' in self.root.objectIds('Silva Folder'))
        self.assertTrue('folder' in self.root.objectIds('Silva Publication'))
        self.assertTrue(verifyObject(IPublication, self.root.folder))
        self.assertTrue('index' in self.root.folder.objectIds())

    def test_publication_to_folder(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')
        self.assertTrue('publication' in self.root.objectIds('Silva Publication'))
        self.assertTrue(verifyObject(IPublication, self.root.publication))

        self.root.publication.to_folder()

        self.assertFalse('publication' in self.root.objectIds('Silva Publication'))
        self.assertTrue('publication' in self.root.objectIds('Silva Folder'))
        self.assertTrue(verifyObject(IFolder, self.root.publication))
        self.assertFalse(IPublication.providedBy(self.root.publication))
        self.assertTrue('index' in self.root.publication.objectIds())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderConvertionTestCase))
    return suite
