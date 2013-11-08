# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import FunctionalLayer
from silva.core.interfaces import IAddableContents
from zope.interface.verify import verifyObject

DEFAULT_ALL_ADDABLES = [
    'Mockup VersionedContent',
    'Mockup Asset',
    'Mockup Non Publishable',
    'Silva Folder',
    'Silva Publication',
    'Silva Image',
    'Silva File',
    'Silva Ghost',
    'Silva Ghost Asset',
    'Silva Ghost Folder',
    'Silva Indexer',
    'Silva Link',
    'Silva AutoTOC']
AUTHOR_ALL_ADDABLES = [
    'Mockup VersionedContent',
    'Mockup Asset',
    'Mockup Non Publishable',
    'Silva Folder',
    'Silva Image',
    'Silva File',
    'Silva Ghost',
    'Silva Ghost Asset',
    'Silva Link',
    'Silva AutoTOC']


class AddablesTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('folder', 'Folder')

    def test_set_and_get_addables(self):
        """Test that if you set addables you get what you set.

        Default value is None.
        """
        self.assertEquals(
            self.root.get_silva_addables_allowed_in_container(),
            None)

        self.root.set_silva_addables_allowed_in_container(
            ['Silva Image'])
        self.assertEquals(
            self.root.get_silva_addables_allowed_in_container(),
            ['Silva Image'])

    def test_addables_all(self):
        """Test adapter: get all addables
        """
        addables = IAddableContents(self.root)
        self.assertTrue(verifyObject(IAddableContents, addables))
        self.assertEqual(addables.get_all_addables(), DEFAULT_ALL_ADDABLES)

        self.root.set_silva_addables_allowed_in_container(
            ['Silva Image', 'Silva File'])

        self.assertEqual(addables.get_all_addables(), DEFAULT_ALL_ADDABLES)

    def test_addables_container(self):
        """Test adapter: get all addables in a given container.

        (Even if you don't have the right to add them).
        """
        folder_addables = IAddableContents(self.root.folder)
        self.assertTrue(verifyObject(IAddableContents, folder_addables))
        self.assertEqual(
            folder_addables.get_container_addables(), DEFAULT_ALL_ADDABLES)

        self.root.set_silva_addables_allowed_in_container(
            ['Silva Publication', 'Silva File'])

        root_addables = IAddableContents(self.root)
        self.assertEqual(
            root_addables.get_container_addables(),
            ['Silva Publication', 'Silva File'])
        folder_addables = IAddableContents(self.root.folder)
        self.assertEqual(
            folder_addables.get_container_addables(),
            ['Silva Publication', 'Silva File'])

    def test_addables_authorized(self):
        """Test adapter: get all authorized addables in a given
        container.

        Author doesn't have the right to add publications.
        """
        folder_addables = IAddableContents(self.root.folder)
        self.assertTrue(verifyObject(IAddableContents, folder_addables))
        self.assertEqual(
            folder_addables.get_authorized_addables(),
            AUTHOR_ALL_ADDABLES)

        self.root.set_silva_addables_allowed_in_container(
            ['Silva Publication', 'Silva File'])

        root_addables = IAddableContents(self.root)
        self.assertEqual(
            root_addables.get_authorized_addables(),
            ['Silva File'])
        folder_addables = IAddableContents(self.root.folder)
        self.assertEqual(
            folder_addables.get_authorized_addables(),
            ['Silva File'])

    def test_root_not_addable(self):
        """Silva Root should never be addable.
        """
        root_addables = IAddableContents(self.root)
        self.assertFalse(
            'Silva Root' in root_addables.get_container_addables())
        self.assertFalse(
            'Silva Root' in root_addables.get_authorized_addables())
        self.assertFalse(
            'Silva Root' in root_addables.get_all_addables())

        folder_addables = IAddableContents(self.root.folder)
        self.assertFalse(
            'Silva Root' in folder_addables.get_container_addables())
        self.assertFalse(
            'Silva Root' in folder_addables.get_authorized_addables())
        self.assertFalse(
            'Silva Root' in folder_addables.get_all_addables())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AddablesTestCase))
    return suite
