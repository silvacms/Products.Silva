# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from zope.component import getUtility

from Acquisition import aq_chain
from Products.Silva.testing import FunctionalLayer

from silva.core.interfaces import IGhostFolder, IGhost
from silva.core.interfaces import IPublication, IFolder
from silva.core.references.interfaces import IReferenceService, IReferenceValue
from silva.core.interfaces import errors
from silva.core.interfaces import IContainerManager


class GhostFolderTestCase(unittest.TestCase):
    """Test the Ghost object.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addFolder('target', 'Target Folder')

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addPublication('publication', 'Publication')
        factory.manage_addMockupVersionedContent('document', 'Document')

        factory = self.root.folder.folder.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')

        factory = self.root.folder.publication.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')
        factory.manage_addFolder('folder', 'Folder')

    def test_ghost_folder(self):
        """Test a Ghost Folder haunting to a Folder.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost', 'Ghost', haunted=self.root.folder)

        ghost = self.root.target.ghost
        folder = self.root.folder
        self.assertTrue(verifyObject(IGhostFolder, ghost))
        self.assertEqual(ghost.get_haunted(), folder)
        self.assertEqual(aq_chain(ghost.get_haunted()), aq_chain(folder))
        self.assertEqual(ghost.get_link_status(), None)

        # Content have been ghost with the same IDS
        self.assertEqual(
            ghost.objectIds(),
            ['document', 'folder', 'index', 'publication'])

        # Folderish content made Ghost folders
        self.assertTrue(verifyObject(IGhostFolder, ghost.folder))
        self.assertEqual(ghost.folder.get_haunted(), folder.folder)
        self.assertEqual(
            aq_chain(ghost.folder.get_haunted()),
            aq_chain(folder.folder))
        self.assertTrue(verifyObject(IGhostFolder, ghost.publication))
        self.assertEqual(
            ghost.publication.get_haunted(),
            folder.publication)
        self.assertEqual(
            aq_chain(ghost.publication.get_haunted()),
            aq_chain(folder.publication))

        # Regular content are ghosts
        self.assertTrue(verifyObject(IGhost, ghost.index))
        self.assertEqual(
            ghost.index.get_haunted(),
            folder.index)
        self.assertTrue(verifyObject(IGhost, ghost.document))
        self.assertEqual(
            ghost.document.get_haunted(),
            folder.document)

        # Ghosted folder was published so the ghost is published as well.
        self.assertTrue(ghost.is_published())

        # Ghost is done recursively
        self.assertEqual(
            ghost.folder.objectIds(),
            ['document'])

        # Ghosted target of this subfodler was not published, so his the ghost
        self.assertFalse(ghost.folder.is_published())

        # Asking the publication on a ghost folder will not return
        # itself (it is not a publication).
        self.assertEqual(ghost.get_publication(), self.root)
        self.assertEqual(ghost.folder.get_publication(), self.root)

    def test_ghost_publication(self):
        """Test a Ghost Folder haunting to a Publication.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost', 'Ghost', haunted=self.root.folder.publication)

        ghost = self.root.target.ghost
        publication = self.root.folder.publication

        self.assertTrue(verifyObject(IGhostFolder, ghost))
        self.assertEqual(ghost.get_link_status(), None)
        self.assertEqual(ghost.get_haunted(), publication)
        self.assertEqual(aq_chain(ghost.get_haunted()), aq_chain(publication))

        # Content have been ghost with the same IDS
        self.assertEqual(
            ghost.objectIds(),
            ['document', 'folder'])

        # If you ask the publication on the ghost folder it will
        # return itself (and if done on a lower ghost folder ghost a
        # folder as well).
        self.assertEqual(ghost.get_publication(), ghost)
        self.assertEqual(ghost.folder.get_publication(), ghost)

    def test_ghost_reference(self):
        """Test the reference created by the ghost.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost', 'Ghost', haunted=self.root.folder)

        ghost = self.root.target.ghost
        folder = self.root.folder

        reference = getUtility(IReferenceService).get_reference(
            ghost, name=u"haunted")
        self.assertTrue(verifyObject(IReferenceValue, reference))
        self.assertEqual(
            aq_chain(reference.target),
            aq_chain(folder))
        self.assertEqual(
            aq_chain(reference.source),
            aq_chain(ghost))

    def test_ghost_to_publication(self):
        """Test convertion of a Ghost Folder to a Publication.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost', 'Ghost', haunted=self.root.folder)

        ghost = self.root.target.ghost
        self.assertFalse(IPublication.providedBy(ghost))
        self.assertTrue(verifyObject(IGhostFolder, ghost))
        self.assertEqual(
            self.root.target.objectValues('Silva Ghost Folder'),
            [ghost])
        self.assertEqual(
            self.root.target.objectValues('Silva Publication'),
            [])

        ghost.to_publication()

        ghost = self.root.target.ghost
        self.assertTrue(verifyObject(IPublication, ghost))
        self.assertFalse(IGhostFolder.providedBy(ghost))
        self.assertEqual(
            self.root.target.objectValues('Silva Ghost Folder'),
            [])
        self.assertEqual(
            self.root.target.objectValues('Silva Publication'),
            [ghost])

        # Content is still there
        self.assertEqual(
            ghost.objectIds(),
            ['document', 'folder', 'index', 'publication'])

        # And there are still ghosts
        self.assertTrue(verifyObject(IGhostFolder, ghost.folder))
        self.assertTrue(verifyObject(IGhostFolder, ghost.publication))
        self.assertTrue(verifyObject(IGhost, ghost.index))
        self.assertTrue(verifyObject(IGhost, ghost.document))

    def test_ghost_to_folder(self):
        """Test Ghost Folder convertion to a regular Folder.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost', 'Ghost', haunted=self.root.folder)

        ghost = self.root.target.ghost
        self.assertTrue(verifyObject(IGhostFolder, ghost))
        self.assertEqual(
            self.root.target.objectValues('Silva Ghost Folder'),
            [ghost])
        self.assertEqual(
            self.root.target.objectValues('Silva Folder'),
            [])

        ghost.to_folder()

        ghost = self.root.target.ghost
        self.assertTrue(verifyObject(IFolder, ghost))
        self.assertFalse(IGhostFolder.providedBy(ghost))
        self.assertEqual(
            self.root.target.objectValues('Silva Ghost Folder'),
            [])
        self.assertEqual(
            self.root.target.objectValues('Silva Folder'),
            [ghost])

        # Content is still there
        self.assertEqual(
            ghost.objectIds(),
            ['document', 'folder', 'index', 'publication'])

        # And there are still ghosts
        self.assertTrue(verifyObject(IGhostFolder, ghost.folder))
        self.assertTrue(verifyObject(IGhostFolder, ghost.publication))
        self.assertTrue(verifyObject(IGhost, ghost.index))
        self.assertTrue(verifyObject(IGhost, ghost.document))

    def test_ghost_modification_time(self):
        """Test Ghost Folder that the modification time is the same
        than the Folder.
        """
        # XXX I don't think this should be the case, maybe more likely
        # the modification datetime of the ghost folder itself, so,
        # the datetime of the last sync.
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder('ghost', 'Ghost')

        ghost = self.root.target.ghost
        self.assertEqual(ghost.get_modification_datetime(), None)

        ghost.set_haunted(self.root.folder)
        self.assertEqual(
            ghost.get_modification_datetime(),
            self.root.folder.get_modification_datetime())

        ghost.set_haunted(0)
        self.assertEqual(ghost.get_modification_datetime(), None)

    def test_ghost_link_status(self):
        """Test Ghost Folder get_link_status. You cannot haunt a Ghost
        Folder unless is link status is correct.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder('ghost', 'Ghost')

        ghost = self.root.target.ghost
        self.assertEqual(
            ghost.get_link_status(),
            errors.EmptyInvalidTarget())

        ghost.set_haunted(self.root.folder.document)
        self.assertEqual(
            ghost.get_link_status(),
            errors.ContainerInvalidTarget())

        ghost.set_haunted(self.root)
        self.assertEqual(
            ghost.get_link_status(),
            errors.CircularInvalidTarget())

        ghost.set_haunted(self.root.target.ghost)
        self.assertEqual(
            ghost.get_link_status(),
            errors.CircularInvalidTarget())

        ghost.set_haunted(self.root.target.folder)
        self.assertEqual(ghost.get_link_status(), None)
        self.assertFalse('folder' in self.root.target.ghost.objectIds())
        ghost.haunt()
        self.assertTrue('folder' in self.root.target.ghost.objectIds())
        ghost.set_haunted(self.root.target.ghost.folder)
        self.assertEqual(
            ghost.get_link_status(),
            errors.CircularInvalidTarget())

        ghost.set_haunted(0)
        self.assertEqual(
            ghost.get_link_status(),
            errors.EmptyInvalidTarget())

    def test_ghost_title(self):
        """Test Ghost Folder title.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder('ghost', 'Ghost')

        ghost = self.root.target.ghost
        self.assertEqual(ghost.get_title_editable(), u'Ghost target is broken')
        self.assertEqual(ghost.get_short_title(), u'Ghost target is broken')
        self.assertEqual(ghost.get_title(), u'Ghost target is broken')

        ghost.set_haunted(self.root.folder)
        self.assertEqual(ghost.get_title_editable(), 'Folder')
        self.assertEqual(ghost.get_short_title(), 'Folder')
        self.assertEqual(ghost.get_title(), 'Folder')

        self.root.folder.set_title('Renamed Folder')
        self.assertEqual(ghost.get_title_editable(), 'Renamed Folder')
        self.assertEqual(ghost.get_short_title(), 'Renamed Folder')
        self.assertEqual(ghost.get_title(), 'Renamed Folder')

    def test_ghost_haunt_differences(self):
        """Test modifications haunting in the source folder.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost', 'Ghost', haunted=self.root.folder)

        ghost = self.root.target.ghost
        folder = self.root.folder

        # Delete content. They are directly removed from the ghost folder.
        self.assertTrue('index' in ghost.objectIds())
        self.assertTrue('folder' in ghost.objectIds())

        with IContainerManager(folder).deleter() as deleter:
            deleter(folder.index)
            deleter(folder.folder)

        self.assertFalse('index' in ghost.objectIds())
        self.assertFalse('folder' in ghost.objectIds())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GhostFolderTestCase))
    return suite
