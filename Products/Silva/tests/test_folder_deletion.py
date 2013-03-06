# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import IContainerManager
from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import ContentError
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer
from Products.Silva.testing import assertTriggersEvents, assertNotTriggersEvents


class AuthorFolderDeletionTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addAutoTOC('toc', 'AutoTOC')
        factory.manage_addPublication('publication', 'Publication')

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('subfolder', 'Sub Folder')
        factory.manage_addAutoTOC('toc', 'AutoTOC')
        factory.manage_addLink('link', 'Link')
        factory.manage_addLink('published_link', 'Published Link')

        IPublicationWorkflow(self.root.folder.published_link).publish()

        self.layer.login(self.user)

    def test_implementation(self):
        manager = IContainerManager(self.root.folder, None)
        self.assertTrue(verifyObject(IContainerManager, manager))
        self.assertNotEqual(manager, None)

        manager = IContainerManager(self.root.toc, None)
        self.assertEqual(manager, None)

    def test_delete_published(self):
        """An author cannot delete published content.
        """
        manager = IContainerManager(self.root.folder)

        with assertNotTriggersEvents(
            'ObjectWillBeRemovedEvent',
            'ObjectRemovedEvent',
            'ContainerModifiedEvent'):
            with manager.deleter() as deleter:
                self.assertIsInstance(
                    deleter(self.root.folder.published_link),
                    ContentError)

        self.assertTrue('published_link' in self.root.folder.objectIds())

    def test_delete_published_recursive(self):
        """An author cannot delete a folder that contains published
        content.
        """
        manager = IContainerManager(self.root)

        with assertNotTriggersEvents(
            'ObjectWillBeRemovedEvent',
            'ObjectRemovedEvent',
            'ContainerModifiedEvent'):
            with manager.deleter() as deleter:
                self.assertIsInstance(
                    deleter(self.root.folder),
                    ContentError)

        self.assertTrue('folder' in self.root.objectIds())

    def test_delete_single(self):
        manager = IContainerManager(self.root.folder)

        with assertTriggersEvents(
            'ObjectWillBeRemovedEvent',
            'ObjectRemovedEvent',
            'ContainerModifiedEvent'):
            with manager.deleter() as deleter:
                self.assertEqual(
                    deleter(self.root.folder.toc),
                    self.root.folder.toc)

        self.assertFalse('toc' in self.root.folder.objectIds())

    def test_delete_multiple(self):
        manager = IContainerManager(self.root.folder)

        with assertTriggersEvents(
            'ObjectWillBeRemovedEvent',
            'ObjectRemovedEvent',
            'ContainerModifiedEvent'):
            with manager.deleter() as deleter:
                self.assertEqual(
                    deleter(self.root.folder.toc),
                    self.root.folder.toc)
                self.assertEqual(
                    deleter(self.root.folder.link),
                    self.root.folder.link)

        self.assertFalse('toc' in self.root.folder.objectIds())
        self.assertFalse('link' in self.root.folder.objectIds())

    def test_delete_invalid(self):
        manager = IContainerManager(self.root.folder)

        with assertNotTriggersEvents(
            'ObjectWillBeRemovedEvent',
            'ObjectRemovedEvent',
            'ContainerModifiedEvent'):
            with manager.deleter() as deleter:
                self.assertIsInstance(
                    deleter(self.root.publication),
                    ContentError)
                self.assertIsInstance(
                    deleter(self.root.toc),
                    ContentError)
                self.assertIsInstance(
                    deleter(self.root.folder),
                    ContentError)

        self.assertTrue('publication' in self.root.objectIds())
        self.assertTrue('toc' in self.root.objectIds())
        self.assertTrue('folder' in self.root.objectIds())


class EditorFolderDeletionTestCase(AuthorFolderDeletionTestCase):
    """Test folder delete as an editor.
    """
    user = 'editor'

    def test_delete_published(self):
        """An editor can delete published content.
        """
        manager = IContainerManager(self.root.folder)

        with assertTriggersEvents(
            'ObjectWillBeRemovedEvent',
            'ObjectRemovedEvent',
            'ContainerModifiedEvent'):
            with manager.deleter() as deleter:
                self.assertEqual(
                    deleter(self.root.folder.published_link),
                    self.root.folder.published_link)

        self.assertFalse('published_link' in self.root.folder.objectIds())

    def test_delete_published_recursive(self):
        """An editor can delete a folder that contains published content.
        """
        manager = IContainerManager(self.root)

        with assertTriggersEvents(
            'ObjectWillBeRemovedEvent',
            'ObjectRemovedEvent',
            'ContainerModifiedEvent'):
            with manager.deleter() as deleter:
                self.assertEqual(
                    deleter(self.root.folder),
                    self.root.folder)

        self.assertFalse('folder' in self.root.objectIds())


class ChiefEditorFolderDeletionTestCase(EditorFolderDeletionTestCase):
    """Test folder management as a chiefeditor.
    """
    user = 'chiefeditor'


class ManagerFolderDeletionTestCase(ChiefEditorFolderDeletionTestCase):
    """Test folder management as a manager.
    """
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorFolderDeletionTestCase))
    suite.addTest(unittest.makeSuite(EditorFolderDeletionTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorFolderDeletionTestCase))
    suite.addTest(unittest.makeSuite(ManagerFolderDeletionTestCase))
    return suite
