# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.ftesting import public_settings
from Products.Silva.testing import FunctionalLayer, tests, Transaction

from silva.core.interfaces import IPublicationWorkflow, IMember
from silva.core.interfaces import IFolder
from zope.interface.verify import verifyObject


class FolderTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')

    def test_implementation(self):
        self.assertTrue(verifyObject(IFolder, self.root.folder))

    def test_get_creation_datetime(self):
        """Test get_creation_datetime. It should be set by default.
        """
        self.assertNotEqual(self.root.folder.get_creation_datetime(), None)
        self.assertNotEqual(self.root.get_creation_datetime(), None)

    def test_creator_and_author_info(self):
        """Test get_creator_info and get_last_author_info.
        """
        creator = self.root.folder.get_creator_info()
        self.assertTrue(verifyObject(IMember, creator))
        self.assertEqual(creator.userid(), 'editor')
        author = self.root.folder.get_last_author_info()
        self.assertTrue(verifyObject(IMember, author))
        self.assertEqual(author.userid(), 'editor')

    def test_get_modification_datetime(self):
        """Test get_creation_datetime
        """
        current_datetime = self.root.folder.get_modification_datetime()
        self.assertNotEqual(current_datetime, None)
        self.assertNotEqual(self.root.get_modification_datetime(), None)
        with Transaction():
            factory = self.root.folder.manage_addProduct['Silva']
            factory.manage_addAutoTOC('index', 'Index')
        self.assertGreater(
            self.root.folder.get_modification_datetime(),
            current_datetime)

    def test_set_title(self):
        """Test set/get title.
        """
        folder = self.root.folder
        self.assertEqual(folder.get_title(), 'Folder')
        self.assertEqual(folder.get_title_or_id(), 'Folder')
        self.assertEqual(folder.get_short_title(), 'Folder')

        folder.set_title('Renamed Folder')
        self.assertEqual(folder.get_title(), 'Renamed Folder')
        self.assertEqual(folder.get_title_or_id(), 'Renamed Folder')
        self.assertEqual(folder.get_short_title(), 'Renamed Folder')

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
        tests.assertContentItemsEqual(
            self.root.folder.get_ordered_publishables(),
            [])

    def test_get_non_publishables_empty(self):
        """Test get_non_publishables without content.
        """
        tests.assertContentItemsEqual(
            self.root.folder.get_non_publishables(),
            [])


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
        with self.layer.open_fixture('torvald.jpg') as image:
            factory.manage_addImage('picture.tif', 'Picture', image)
        factory.manage_addFolder('folder', 'Folder')
        with self.layer.open_fixture('test_document.xml') as data:
            factory.manage_addFile('data_file.xml', 'Data file', data)
        factory.manage_addPublication('publication', 'Publication')

    def test_public_view(self):
        """Render a folder publicly.
        """
        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(
                browser.open('http://localhost/root/folder'),
                200)
            self.assertEqual(
                browser.inspect.content,
                ['This container has no index.'])

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('index', 'Index')
        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(
                browser.open('http://localhost/root/folder'),
                200)
            self.assertEqual(
                browser.inspect.content,
                ['This container has no index.'])

        IPublicationWorkflow(self.root.folder.index).publish()
        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(
                browser.open('http://localhost/root/folder'),
                200)
            self.assertEqual(
                browser.inspect.content,
                ['Index'])

    def test_get_ordered_publishables(self):
        """Test get_ordered_publishables with content.
        """
        tests.assertContentItemsEqual(
            self.root.folder.get_ordered_publishables(),
            [self.root.folder['first_link'],
             self.root.folder['second_link'],
             self.root.folder['folder'],
             self.root.folder['publication']])

    def test_get_non_publishables(self):
        """Test get_non_publishables with content.
        """
        tests.assertContentItemsEqual(
            self.root.folder.get_non_publishables(),
            [self.root.folder['data_file.xml'],
             self.root.folder['picture.tif']])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderTestCase))
    suite.addTest(unittest.makeSuite(FolderWithContentTestCase))
    return suite
