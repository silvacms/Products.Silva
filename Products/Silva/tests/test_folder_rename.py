# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core.interfaces import IContainerManager
from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import IAutoTOC, ILink, IFolder
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer
from Products.Silva.testing import assertTriggersEvents, assertNotTriggersEvents


class AuthorFolderRenameTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login(self.user)

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('toc', 'AutoTOC')
        factory.manage_addLink('link', 'Link')
        factory.manage_addLink('published_link', 'Published Link')

        IPublicationWorkflow(self.root.folder.published_link).publish()

    def test_rename_id_and_title(self):
        """Rename identifier and title for a single non-publishable item.
        """
        manager = IContainerManager(self.root.folder)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.renamer() as renamer:
                self.assertNotEqual(
                    renamer.add((self.root.folder.toc, 'newtoc', 'New AutoTOC')),
                    None)

        self.assertFalse('toc' in self.root.folder.objectIds())
        self.assertTrue('newtoc' in self.root.folder.objectIds())
        self.assertTrue(verifyObject(IAutoTOC, self.root.folder.newtoc))
        self.assertEqual(self.root.folder.newtoc.get_title(), 'New AutoTOC')

    def test_rename_id(self):
        """Rename only the identifier for a single non-publishable item.
        """
        manager = IContainerManager(self.root.folder)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.renamer() as renamer:
                self.assertNotEqual(
                    renamer.add((self.root.folder.toc, 'newtoc', None)),
                    None)

        self.assertFalse('toc' in self.root.folder.objectIds())
        self.assertTrue('newtoc' in self.root.folder.objectIds())
        self.assertTrue(verifyObject(IAutoTOC, self.root.folder.newtoc))
        self.assertEqual(self.root.folder.newtoc.get_title(), 'AutoTOC')

    def test_rename_title(self):
        """Rename only the title for a single non-publishable item.
        """
        manager = IContainerManager(self.root.folder)
        with assertNotTriggersEvents('ObjectWillBeMovedEvent',
                                     'ObjectMovedEvent',
                                     'ContainerModifiedEvent'):
            with manager.renamer() as renamer:
                self.assertNotEqual(
                    renamer.add((self.root.folder.toc, None, 'New AutoTOC')),
                    None)

        self.assertTrue('toc' in self.root.folder.objectIds())
        self.assertTrue(verifyObject(IAutoTOC, self.root.folder.toc))
        self.assertEqual(self.root.folder.toc.get_title(), 'New AutoTOC')

    def test_rename_multiple(self):
        """Rename multipe content in one time.
        """
        manager = IContainerManager(self.root.folder)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.renamer() as renamer:
                self.assertNotEqual(
                    renamer.add((self.root.folder.toc, 'newtoc', None)),
                    None)
                self.assertNotEqual(
                    renamer.add((self.root.folder.link, 'nice_link', 'Nice Link')),
                    None)

        self.assertFalse('toc' in self.root.folder.objectIds())
        self.assertTrue('newtoc' in self.root.folder.objectIds())
        self.assertTrue(verifyObject(IAutoTOC, self.root.folder.newtoc))
        self.assertEqual(self.root.folder.newtoc.get_title(), 'AutoTOC')
        self.assertFalse('link' in self.root.folder.objectIds())
        self.assertTrue('nice_link' in self.root.folder.objectIds())
        self.assertTrue(verifyObject(ILink, self.root.folder.nice_link))
        self.assertEqual(self.root.folder.nice_link.get_editable().get_title(), 'Nice Link')

    def test_rename_not_published_content_id_and_title(self):
        """Rename id and title for a not published content.
        """
        manager = IContainerManager(self.root.folder)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.renamer() as renamer:
                self.assertNotEqual(
                    renamer.add((self.root.folder.link, 'nice_link', 'Nice Link')),
                    None)

        self.assertFalse('link' in self.root.folder.objectIds())
        self.assertTrue('nice_link' in self.root.folder.objectIds())
        self.assertTrue(verifyObject(ILink, self.root.folder.nice_link))
        self.assertEqual(self.root.folder.nice_link.get_editable().get_title(), 'Nice Link')

    def test_rename_published_content_id_and_title(self):
        """Rename a published content id and title.

        An author can't do anything, nothing is done.
        """
        manager = IContainerManager(self.root.folder)
        with assertNotTriggersEvents('ObjectWillBeMovedEvent',
                                     'ObjectMovedEvent',
                                     'ContainerModifiedEvent'):
            with manager.renamer() as renamer:
                self.assertEqual(
                    renamer.add((self.root.folder.published_link, 'updated_link', 'Updated Link')),
                    None)

        self.assertTrue('published_link' in self.root.folder.objectIds())
        self.assertFalse('updated_link' in self.root.folder.objectIds())
        self.assertTrue(verifyObject(ILink, self.root.folder.published_link))
        self.assertEqual(self.root.folder.published_link.get_title(), 'Published Link')

    def test_rename_published_container_id_and_title(self):
        """Rename a published container it and title.

        An author can only change the title.
        """
        manager = IContainerManager(self.root)
        with assertNotTriggersEvents('ObjectWillBeMovedEvent',
                                     'ObjectMovedEvent',
                                     'ContainerModifiedEvent'):
            with manager.renamer() as renamer:
                self.assertNotEqual(
                    renamer.add((self.root.folder, 'archives', 'Archives')),
                    None)

        self.assertTrue('folder' in self.root.objectIds())
        self.assertFalse('archives' in self.root.objectIds())
        self.assertTrue(verifyObject(IFolder, self.root.folder))
        # Author got the permission to change the title.
        self.assertEqual(self.root.folder.get_title(), 'Archives')


class EditorFolderRenameTestCase(AuthorFolderRenameTestCase):
    user = 'editor'

    def test_rename_published_content_id_and_title(self):
        """Rename a published content id and title.

        An Editor has the right to change both the id and title.
        """
        manager = IContainerManager(self.root.folder)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.renamer() as renamer:
                self.assertNotEqual(
                    renamer.add((self.root.folder.published_link, 'updated_link', 'Updated Link')),
                    None)

        self.assertFalse('published_link' in self.root.folder.objectIds())
        self.assertTrue('updated_link' in self.root.folder.objectIds())
        self.assertTrue(verifyObject(ILink, self.root.folder.updated_link))
        # The title is not changed (it changed only the editable version, there is None)
        self.assertEqual(self.root.folder.updated_link.get_title(), 'Published Link')

    def test_rename_published_container_id_and_title(self):
        """Rename a published container id and title.

        An Editor has the right to change both the id and title.
        """
        manager = IContainerManager(self.root)
        with assertTriggersEvents('ObjectWillBeMovedEvent',
                                  'ObjectMovedEvent',
                                  'ContainerModifiedEvent'):
            with manager.renamer() as renamer:
                self.assertNotEqual(
                    renamer.add((self.root.folder, 'archives', 'Archives')),
                    None)

        self.assertFalse('folder' in self.root.objectIds())
        self.assertTrue('archives' in self.root.objectIds())
        self.assertTrue(verifyObject(IFolder, self.root.archives))
        self.assertEqual(self.root.archives.get_title(), 'Archives')


class ChiefEditorFolderRenameTestCase(EditorFolderRenameTestCase):
    user = 'chiefeditor'


class ManagerFolderRenameTestCase(ChiefEditorFolderRenameTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorFolderRenameTestCase))
    suite.addTest(unittest.makeSuite(EditorFolderRenameTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorFolderRenameTestCase))
    suite.addTest(unittest.makeSuite(ManagerFolderRenameTestCase))
    return suite
