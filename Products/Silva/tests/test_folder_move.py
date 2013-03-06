# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import IContainerManager
from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import IAutoTOC, ILink, IFolder
from silva.core.interfaces import ContainerError, ContentError
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer
from Products.Silva.testing import assertTriggersEvents, assertNotTriggersEvents


class AuthorFolderMovingTestCase(unittest.TestCase):
    """Test API to move content between folders.
    """
    layer = FunctionalLayer
    user = 'author'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

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

    def test_move_content(self):
        """Move a single item.
        """
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.mover() as mover:
                self.assertNotEqual(
                    mover(self.root.source.toc),
                    None)

        self.assertFalse('toc' in self.root.source.objectIds())
        self.assertTrue('toc' in self.root.target.objectIds())
        self.assertTrue(verifyObject(IAutoTOC, self.root.target.toc))

    def test_move_content_same_container(self):
        """Move a single content into the same container than it is
        already there.
        """
        manager = IContainerManager(self.root.source)
        with assertNotTriggersEvents('ObjectWillBeMovedEvent',
                                     'ObjectMovedEvent',
                                     'ContainerModifiedEvent'):
            with manager.mover() as mover:
                self.assertIsInstance(
                    mover(self.root.source.toc),
                    ContainerError)

        self.assertTrue('toc' in self.root.source.objectIds())

    def test_move_content_id_already_in_use(self):
        """Move a content with an id that is already in use in the
        target folder.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addLink('toc', 'Link to AutoTOC')
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.mover() as mover:
                self.assertNotEqual(
                    mover(self.root.source.toc),
                    None)

        self.assertFalse('toc' in self.root.source.objectIds())
        self.assertTrue('toc' in self.root.target.objectIds())
        self.assertTrue('move_of_toc' in self.root.target.objectIds())
        self.assertTrue(verifyObject(ILink, self.root.target.toc))
        self.assertTrue(verifyObject(IAutoTOC, self.root.target.move_of_toc))

        # Now if we move it back, the move_of_ will be stripped
        manager = IContainerManager(self.root.source)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.mover() as mover:
                self.assertNotEqual(
                    mover(self.root.target.move_of_toc),
                    None)

        self.assertTrue('toc' in self.root.source.objectIds())
        self.assertFalse('move_of_toc' in self.root.target.objectIds())
        self.assertTrue(verifyObject(IAutoTOC, self.root.source.toc))

    def test_move_not_addable_content(self):
        """Move a content that is not addable in the target folder.

        This should not be possible (for everybody).
        """
        self.root.target.set_silva_addables_allowed_in_container(
            ['Silva Image', 'Silva File'])

        manager = IContainerManager(self.root.target)
        with assertNotTriggersEvents('ObjectWillBeMovedEvent',
                                     'ObjectMovedEvent',
                                     'ContainerModifiedEvent'):
            with manager.mover() as mover:
                self.assertIsInstance(
                    mover(self.root.source.toc),
                    ContainerError)

        self.assertTrue('toc' in self.root.source.objectIds())
        self.assertEqual(self.root.target.objectIds(), [])
        self.assertTrue(verifyObject(IAutoTOC, self.root.source.toc))

    def test_move_multiple(self):
        """Move multiple content in one time (one container, one
        unpublished content).
        """
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.mover() as mover:
                self.assertNotEqual(
                    mover(self.root.source.folder),
                    None)
                self.assertNotEqual(
                    mover(self.root.source.link),
                    None)

        self.assertFalse('folder' in self.root.source.objectIds())
        self.assertTrue('folder' in self.root.target.objectIds())
        self.assertTrue(verifyObject(IFolder, self.root.target.folder))
        self.assertFalse('link' in self.root.source.objectIds())
        self.assertTrue('link' in self.root.target.objectIds())
        self.assertTrue(verifyObject(ILink, self.root.target.link))

    def test_move_published_content(self):
        """Move a single published content.

        Authors doesn't have the right to do it. The link stays published.
        """
        manager = IContainerManager(self.root.target)
        with assertNotTriggersEvents('ObjectWillBeMovedEvent',
                                     'ObjectMovedEvent',
                                     'ContainerModifiedEvent'):
            with manager.mover() as mover:
                self.assertIsInstance(
                    mover(self.root.source.published_link),
                    ContentError)

        self.assertTrue('published_link' in self.root.source.objectIds())
        self.assertFalse('published_link' in self.root.target.objectIds())
        self.assertTrue(verifyObject(ILink, self.root.source.published_link))
        self.assertNotEqual(self.root.source.published_link.get_viewable(), None)

    def test_move_published_container(self):
        """Move a single published container.

        Authors doesn't have the right to do it.
        """
        manager = IContainerManager(self.root.target)
        with assertNotTriggersEvents('ObjectWillBeMovedEvent',
                                     'ObjectMovedEvent',
                                     'ContainerModifiedEvent'):
            with manager.mover() as mover:
                self.assertIsInstance(
                    mover(self.root.source),
                    ContentError)

        self.assertTrue('source' in self.root.objectIds())
        self.assertFalse('source' in self.root.target.objectIds())
        self.assertTrue(verifyObject(IFolder, self.root.source))


class EditorFolderMovingTestCase(AuthorFolderMovingTestCase):
    user = 'editor'

    def test_move_published_content(self):
        """Move a single published content.

        Editors can do it. The link stays published.
        """
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.mover() as mover:
                self.assertNotEqual(
                    mover(self.root.source.published_link),
                    None)

        self.assertFalse('published_link' in self.root.source.objectIds())
        self.assertTrue('published_link' in self.root.target.objectIds())
        self.assertTrue(verifyObject(ILink, self.root.target.published_link))
        self.assertNotEqual(self.root.target.published_link.get_viewable(), None)

    def test_move_published_container(self):
        """Move a single published container.

        Authors doesn't have the right to do it.
        """
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.mover() as mover:
                self.assertNotEqual(
                    mover(self.root.source),
                    None)

        self.assertFalse('source' in self.root.objectIds())
        self.assertTrue('source' in self.root.target.objectIds())
        self.assertTrue(verifyObject(IFolder, self.root.target.source))
        # Inner content is still there and published.
        self.assertItemsEqual(
            self.root.target.source.objectIds(),
            ['toc', 'link', 'published_link', 'folder'])
        self.assertNotEqual(self.root.target.source.published_link.get_viewable(), None)


class ChiefEditorFolderMovingTestCase(EditorFolderMovingTestCase):
    user = 'chiefeditor'


class ManagerMovingTestCase(ChiefEditorFolderMovingTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorFolderMovingTestCase))
    suite.addTest(unittest.makeSuite(EditorFolderMovingTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorFolderMovingTestCase))
    suite.addTest(unittest.makeSuite(ManagerMovingTestCase))
    return suite
