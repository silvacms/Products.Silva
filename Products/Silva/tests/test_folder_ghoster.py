# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import IContainerManager, IPublicationWorkflow
from silva.core.interfaces import IGhost, IGhostVersion, IGhostAsset, IGhostFolder
from silva.core.interfaces.errors import IContentErrorBundle
from zope.interface.verify import verifyObject

from Products.Silva.testing import assertTriggersEvents
from Products.Silva.testing import FunctionalLayer, Transaction
from Products.Silva.tests.mockers import IMockupNonPublishable


class EditorFolderGhosterTestCase(unittest.TestCase):
    """Test API to paste as a ghost inside a folder.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('source', 'Source Folder')
            factory.manage_addFolder('target', 'Target Folder')
            factory = self.root.source.manage_addProduct['Silva']
            factory.manage_addAutoTOC('toc', 'AutoTOC')
            factory.manage_addMockupVersionedContent('data', 'Data')
            factory.manage_addFolder('folder', 'Folder')
            with self.layer.open_fixture('silva.png') as stream:
                factory.manage_addFile('logo', 'Silva Logo', stream)

            IPublicationWorkflow(self.root.source.data).publish()

    def test_invalid(self):
        """Pasting a content as a ghost folder that contains a content
        with an invalid identifier.
        """
        self.root.source.manage_renameObject('folder', 'index')
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectWillBeAddedEvent',
                                  'ObjectAddedEvent',
                                  'ContainerModifiedEvent'):
            with manager.ghoster() as ghoster:
                error = ghoster(self.root.source)

        self.assertTrue(verifyObject(IContentErrorBundle, error))
        self.assertEqual(error.content, self.root.target.source)
        self.assertEqual(error.reason, u'Error while synchronizing the Ghost Folder: not all its content have been updated properly.')
        self.assertEqual(len(error.errors), 1)

    def test_other(self):
        """Pasting a content that doesn't have a ghost
        implementation. It should be copied.
        """
        factory = self.root.source.manage_addProduct['Silva']
        factory.manage_addMockupNonPublishable('stuff', 'Stuff')
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectWillBeAddedEvent',
                                  'ObjectAddedEvent',
                                  'ContainerModifiedEvent'):
            with manager.ghoster() as ghoster:
                ghost = ghoster(self.root.source.stuff)

        self.assertTrue(verifyObject(IMockupNonPublishable, ghost))
        self.assertIn('stuff', self.root.target.objectIds())

    def test_asset(self):
        """Pasting an asset as a ghost asset.
        """
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectWillBeAddedEvent',
                                  'ObjectAddedEvent',
                                  'ContainerModifiedEvent'):
            with manager.ghoster() as ghoster:
                ghost = ghoster(self.root.source.logo)

        self.assertTrue(verifyObject(IGhostAsset, ghost))
        self.assertIn('logo', self.root.target.objectIds())
        self.assertEqual(ghost.get_link_status(), None)
        self.assertEqual(ghost.get_haunted(), self.root.source.logo)

    def test_content(self):
        """When pasting a content as a regular ghost, it doesn't get
        published.
        """
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectWillBeAddedEvent',
                                  'ObjectAddedEvent',
                                  'ContainerModifiedEvent'):
            with manager.ghoster() as ghoster:
                ghost = ghoster(self.root.source.data)

        self.assertTrue(verifyObject(IGhost, ghost))
        self.assertIn('data', self.root.target.objectIds())
        self.assertEqual(ghost.get_haunted(), self.root.source.data)
        self.assertEqual(ghost.is_published(), False)
        self.assertEqual(ghost.get_viewable(), None)

        version = ghost.get_editable()
        self.assertTrue(verifyObject(IGhostVersion, version))
        self.assertEqual(version.get_link_status(), None)
        self.assertEqual(version.get_haunted(), self.root.source.data)

    def test_folder(self):
        """When pasting a folder as a ghost, its content is ghosted
        and any versioned content (ghost) in it are published.
        """
        manager = IContainerManager(self.root.target)
        with assertTriggersEvents('ObjectWillBeAddedEvent',
                                  'ObjectAddedEvent',
                                  'ContainerModifiedEvent'):
            with manager.ghoster() as ghoster:
                ghost = ghoster(self.root.source)

        self.assertTrue(verifyObject(IGhostFolder, ghost))
        self.assertEqual(ghost.get_link_status(), None)
        self.assertEqual(ghost.get_haunted(), self.root.source)
        self.assertIn('source', self.root.target.objectIds())

        # The ghost folder is created inside the target folder and is
        # already haunting the source.
        ghost = self.root.target.source
        self.assertTrue(verifyObject(IGhostFolder, ghost))
        self.assertEqual(ghost.get_link_status(), None)
        self.assertEqual(ghost.get_haunted(), self.root.source)
        self.assertItemsEqual(
            ghost.objectIds(),
            ['toc', 'data', 'folder', 'logo'])
        self.assertTrue(verifyObject(IGhost, ghost.toc))
        self.assertEqual(ghost.toc.get_haunted(), self.root.source.toc)
        self.assertTrue(verifyObject(IGhost, ghost.data))
        self.assertEqual(ghost.data.get_haunted(), self.root.source.data)
        self.assertEqual(ghost.data.is_published(), True)
        self.assertTrue(verifyObject(IGhostFolder, ghost.folder))
        self.assertEqual(ghost.folder.get_haunted(), self.root.source.folder)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EditorFolderGhosterTestCase))
    return suite
