# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer
from Products.Silva.tests.helpers import open_test_file

from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import IFolder
from zope.interface.verify import verifyObject


class FolderTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
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
        self.assertFalse(self.root.folder.is_published())
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addLink('index', 'Link')
        self.assertFalse(self.root.folder.is_published())

        # Publish the default to publish the folder
        IPublicationWorkflow(self.root.folder.get_default()).publish()
        self.assertTrue(self.root.folder.is_published())

        # Close the default close the folder.
        IPublicationWorkflow(self.root.folder.get_default()).close()
        self.assertFalse(self.root.folder.is_published())

    def test_get_ordered_publishables_empty(self):
        """Test get_ordered_publishables without content.
        """
        self.assertEqual(self.root.folder.get_ordered_publishables(), [])

    def test_get_non_publishables_empty(self):
        """Test get_non_publishables without content.
        """
        self.assertEqual(self.root.folder.get_non_publishables(), [])


class FolderWithContentTestCase(unittest.TestCase):
    """Test folder API when it have some contents.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addLink('first_link', 'First Link')
        factory.manage_addLink('second_link', 'Second Link')
        with open_test_file('torvald.jpg') as image:
            factory.manage_addImage('picture.tif', 'Picture', image)
        factory.manage_addFolder('folder', 'Folder')
        with open_test_file('test_document.xml') as data:
            factory.manage_addFile('data_file.xml', 'Data file', data)
        factory.manage_addPublication('publication', 'Publication')

    def test_get_ordered_publishables(self):
        """Test get_ordered_publishables with content.
        """
        self.assertEqual(
            self.root.folder.get_ordered_publishables(),
            [self.root.folder['first_link'],
             self.root.folder['second_link'],
             self.root.folder['folder'],
             self.root.folder['publication']])

    def test_get_non_publishables(self):
        """Test get_non_publishables with content.
        """
        self.assertItemsEqual(
            self.root.folder.get_non_publishables(),
            [self.root.folder['data_file.xml'],
             self.root.folder['picture.tif']])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderTestCase))
    suite.addTest(unittest.makeSuite(FolderWithContentTestCase))
    return suite
