# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import IContainerManager, ContainerError
from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import IAutoTOC, ILink, IFolder
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer, Transaction
from Products.Silva.testing import assertTriggersEvents, assertNotTriggersEvents


class AuthorFolderCopyTestCase(unittest.TestCase):
    """Test API to copy between folders.
    """
    layer = FunctionalLayer
    user = 'author'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('source', 'Source Folder')
            factory.manage_addFolder('target', 'Target Folder')

            factory = self.root.source.manage_addProduct['Silva']
            factory.manage_addAutoTOC('toc', 'AutoTOC')
            factory.manage_addLink('link', 'Link')
            factory.manage_addLink('published_link', 'Published Link')
            factory.manage_addFolder('folder', 'Folder')

            IPublicationWorkflow(self.root.source.published_link).publish()

        self.layer.login(self.user)

    def test_copy_content(self):
        """Copy a single content.
        """
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectCopiedEvent',
                                  'ObjectWillBeAddedEvent',
                                  'ObjectAddedEvent',
                                  'ContainerModifiedEvent',
                                  'ObjectClonedEvent'):
            with manager.copier() as copier:
                self.assertNotEqual(copier(self.root.source.toc), None)

        self.assertTrue('toc' in self.root.source.objectIds())
        self.assertTrue('toc' in self.root.target.objectIds())
        self.assertTrue(verifyObject(IAutoTOC, self.root.target.toc))
        self.assertEqual(self.root.target.toc.get_title(), 'AutoTOC')

    def test_copy_content_id_already_in_use(self):
        """Copy a single content to a folder where the content id is
        already in use.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addLink('folder', 'Link to the ultimate Folder')

        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectCopiedEvent',
                                  'ObjectWillBeAddedEvent',
                                  'ObjectAddedEvent',
                                  'ContainerModifiedEvent',
                                  'ObjectClonedEvent'):
            with manager.copier() as copier:
                self.assertNotEqual(copier(self.root.source.folder), None)

        self.assertTrue('folder' in self.root.source.objectIds())
        self.assertTrue('folder' in self.root.target.objectIds())
        self.assertTrue('copy_of_folder' in self.root.target.objectIds())
        self.assertTrue(verifyObject(ILink, self.root.target.folder))
        self.assertTrue(verifyObject(IFolder, self.root.target.copy_of_folder))

        # And an another time will create a copy2_of_folder
        with assertTriggersEvents('ObjectCopiedEvent',
                                  'ObjectWillBeAddedEvent',
                                  'ObjectAddedEvent',
                                  'ContainerModifiedEvent',
                                  'ObjectClonedEvent'):
            with manager.copier() as copier:
                self.assertNotEqual(copier(self.root.source.folder), None)

        self.assertTrue('copy2_of_folder' in self.root.target.objectIds())
        self.assertTrue(verifyObject(IFolder, self.root.target.copy2_of_folder))

    def test_copy_not_addable_content(self):
        """Move a content that is not addable in the target folder.

        This should not be possible (for everybody).
        """
        self.root.target.set_silva_addables_allowed_in_container(
            ['Silva Image', 'Silva File'])

        manager = IContainerManager(self.root.target)
        with assertNotTriggersEvents('ObjectWillBeMovedEvent',
                                     'ObjectMovedEvent',
                                     'ContainerModifiedEvent'):
            with manager.copier() as copier:
                self.assertIsInstance(
                    copier(self.root.source.toc),
                    ContainerError)

        self.assertEqual(self.root.target.objectIds(), [])

    def test_copy_published_content(self):
        """Copy a content that is published. It is copied, but the
        copy will be closed.
        """
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectCopiedEvent',
                                  'ObjectWillBeAddedEvent',
                                  'ObjectAddedEvent',
                                  'ContainerModifiedEvent',
                                  'ObjectClonedEvent'):
            with manager.copier() as copier:
                self.assertNotEqual(copier(self.root.source.published_link), None)

        self.assertTrue('published_link' in self.root.source.objectIds())
        self.assertTrue('published_link' in self.root.target.objectIds())
        self.assertTrue(verifyObject(ILink, self.root.target.published_link))
        self.assertEqual(self.root.target.published_link.get_viewable(), None)
        self.assertNotEqual(self.root.source.published_link.get_viewable(), None)

    def test_copy_published_container(self):
        """Copy a container that contains published content. All
        content will be copied, and published content will be closed.
        """
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectCopiedEvent',
                                  'ObjectWillBeAddedEvent',
                                  'ObjectAddedEvent',
                                  'ContainerModifiedEvent',
                                  'ObjectClonedEvent'):
            with manager.copier() as copier:
                self.assertNotEqual(copier(self.root.source), None)

        self.assertTrue('source' in self.root.target.objectIds())
        self.assertItemsEqual(
            self.root.target.source.objectIds(),
            ['folder', 'link', 'published_link', 'toc'])
        self.assertTrue(verifyObject(IFolder, self.root.target.source))
        self.assertTrue(verifyObject(IAutoTOC, self.root.target.source.toc))
        self.assertTrue(verifyObject(ILink, self.root.target.source.link))
        self.assertTrue(verifyObject(ILink, self.root.target.source.published_link))
        self.assertEqual(self.root.target.source.link.get_viewable(), None)
        self.assertEqual(self.root.target.source.published_link.get_viewable(), None)


class EditorFolderCopyTestCase(AuthorFolderCopyTestCase):
    user = 'editor'


class ChiefEditorFolderCopyTestCase(EditorFolderCopyTestCase):
    user = 'chiefeditor'


class ManagerFolderCopyTestCase(ChiefEditorFolderCopyTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorFolderCopyTestCase))
    suite.addTest(unittest.makeSuite(EditorFolderCopyTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorFolderCopyTestCase))
    suite.addTest(unittest.makeSuite(ManagerFolderCopyTestCase))
    return suite


