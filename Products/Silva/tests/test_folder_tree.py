# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import IAccessSecurity
from silva.core.interfaces import ITreeContents, IPublicationWorkflow
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer


class FolderTreeTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')
        factory.manage_addMockupVersionedContent('document', 'Document')
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addPublication('publication', 'Publication')

        with self.layer.open_fixture('testimage.gif') as image_file:
            factory.manage_addImage('image', 'Image', image_file)

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')
        factory.manage_addMockupVersionedContent('document', 'Document')
        factory.manage_addFolder('folder', 'Folder')

        factory = self.root.folder.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')
        factory.manage_addMockupVersionedContent('document', 'Document')

        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')
        factory.manage_addMockupVersionedContent('document', 'Document')


    def test_implementation(self):
        root_tree = ITreeContents(self.root)
        self.assertTrue(verifyObject(ITreeContents, root_tree))

        folder_tree = ITreeContents(self.root.folder)
        self.assertTrue(verifyObject(ITreeContents, folder_tree))

    def test_get_tree(self):
        self.assertEqual(
            ITreeContents(self.root).get_tree(),
            [(0, self.root.document),
             (0, self.root.folder),
             (1, self.root.folder.document),
             (1, self.root.folder.folder),
             (2, self.root.folder.folder.document),
             (0, self.root.publication)])

    def test_get_container_tree(self):
        self.assertEqual(
            ITreeContents(self.root).get_container_tree(),
            [(0, self.root.folder),
             (1, self.root.folder.folder),
             (0, self.root.publication)])

    def test_get_public_tree(self):
        self.assertEqual(
            ITreeContents(self.root).get_public_tree(),
            [(0, self.root.folder),
             (1, self.root.folder.folder),
             (0, self.root.publication)])
        self.assertEqual(
            ITreeContents(self.root).get_public_tree(1),
            [(0, self.root.folder),
             (1, self.root.folder.folder),
             (0, self.root.publication)])
        self.assertEqual(
            ITreeContents(self.root).get_public_tree(0),
            [(0, self.root.folder),
             (0, self.root.publication)])
        IPublicationWorkflow(self.root.document).publish()
        IPublicationWorkflow(self.root.publication.document).publish()
        self.assertEqual(
            ITreeContents(self.root).get_public_tree(),
            [(0, self.root.document),
             (0, self.root.folder),
             (1, self.root.folder.folder),
             (0, self.root.publication)])
        IAccessSecurity(self.root.folder).minimum_role = 'Manager'
        self.assertEqual(
            ITreeContents(self.root).get_public_tree(),
            [(0, self.root.document),
             (0, self.root.publication)])

    def test_get_public_tree_all(self):
        self.assertEqual(
            ITreeContents(self.root).get_public_tree_all(),
            [(0, self.root.folder),
             (1, self.root.folder.folder),
             (0, self.root.publication)])
        IPublicationWorkflow(self.root.document).publish()
        IPublicationWorkflow(self.root.publication.document).publish()
        self.assertEqual(
            ITreeContents(self.root).get_public_tree_all(),
            [(0, self.root.document),
             (0, self.root.folder),
             (1, self.root.folder.folder),
             (0, self.root.publication),
             (1, self.root.publication.document)])

    def test_get_status_tree(self):
        self.assertEqual(
            ITreeContents(self.root).get_status_tree(),
            [(0, self.root.index),
             (0, self.root.document),
             (0, self.root.folder),
             (1, self.root.folder.index),
             (1, self.root.folder.document),
             (1, self.root.folder.folder),
             (2, self.root.folder.folder.index),
             (2, self.root.folder.folder.document),
             (0, self.root.publication)])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderTreeTestCase))
    return suite
