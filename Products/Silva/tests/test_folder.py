# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer

from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import IFolder
from zope.interface.verify import verifyObject


class FolderTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

    def test_implementation(self):
        self.assertTrue(verifyObject(IFolder, self.root.folder))

    def test_get_default(self):
        """get_default return the index object of the container if it
        exist or None.
        """
        self.assertEqual(self.root.folder.get_default(), None)
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Table of Content')
        self.assertEqual(self.root.folder.get_default(), self.root.folder.index)

    def test_is_published(self):
        """A folder is published if there is a published index.
        """
        self.assertEqual(self.root.folder.is_published(), False)
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addLink('index', 'Link')
        self.assertEqual(self.root.folder.is_published(), False)
        IPublicationWorkflow(self.root.folder.get_default()).publish()
        self.assertEqual(self.root.folder.is_published(), True)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderTestCase))
    return suite
