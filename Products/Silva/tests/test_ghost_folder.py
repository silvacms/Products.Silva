# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from zope.component import getUtility

from Acquisition import aq_chain
from Products.Silva.testing import FunctionalLayer
from Products.Silva.tests.mockers import IMockupAsset

from silva.core.interfaces import IContainerManager, IPublicationWorkflow
from silva.core.interfaces import IGhostFolder, IGhost
from silva.core.interfaces import IPublication, IFolder
from silva.core.interfaces import errors
from silva.core.references.interfaces import IReferenceService, IReferenceValue


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
        factory.manage_addGhostFolder('ghost', None, haunted=self.root.folder)

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
        self.assertEqual(ghost.folder.get_link_status(), None)
        self.assertTrue(verifyObject(IGhostFolder, ghost.publication))
        self.assertEqual(
            ghost.publication.get_haunted(),
            folder.publication)
        self.assertEqual(
            aq_chain(ghost.publication.get_haunted()),
            aq_chain(folder.publication))
        self.assertEqual(ghost.publication.get_link_status(), None)

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
        self.assertEqual(ghost.document.get_viewable().get_link_status(), None)

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
            'ghost', None, haunted=self.root.folder.publication)

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
        factory.manage_addGhostFolder('ghost', None, haunted=self.root.folder)

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
        factory.manage_addGhostFolder('ghost', None, haunted=self.root.folder)

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
        factory.manage_addGhostFolder('ghost', None, haunted=self.root.folder)

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
        factory.manage_addGhostFolder('ghost', None)

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
        factory.manage_addGhostFolder('ghost', None)

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
        factory.manage_addGhostFolder('ghost', None)

        ghost = self.root.target.ghost
        self.assertEqual(ghost.get_title_editable(), u'Ghost target is broken')
        self.assertEqual(ghost.get_title(), u'Ghost target is broken')
        self.assertEqual(ghost.get_short_title_editable(), u'Ghost target is broken')
        self.assertEqual(ghost.get_short_title(), u'Ghost target is broken')

        ghost.set_haunted(self.root.folder)
        self.assertEqual(ghost.get_title_editable(), 'Folder')
        self.assertEqual(ghost.get_title(), 'Folder')
        self.assertEqual(ghost.get_short_title_editable(), 'Folder')
        self.assertEqual(ghost.get_short_title(), 'Folder')

        self.root.folder.set_title('Renamed Folder')
        self.assertEqual(ghost.get_title_editable(), 'Renamed Folder')
        self.assertEqual(ghost.get_title(), 'Renamed Folder')
        self.assertEqual(ghost.get_short_title_editable(), 'Renamed Folder')
        self.assertEqual(ghost.get_short_title(), 'Renamed Folder')

        # An empty folder will not be published.
        ghost.set_haunted(self.root.target)
        self.assertEqual(ghost.get_title_editable(), 'Target Folder')
        self.assertEqual(ghost.get_title(), 'Ghost target is broken')
        self.assertEqual(ghost.get_short_title_editable(), 'Target Folder')
        self.assertEqual(ghost.get_short_title(), 'Ghost target is broken')

    def test_ghost_haunt_remove_ghosts(self):
        """Test modifications: removing content in the target remove
        corresponding ghosts from the ghost folder.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder('ghost', None, haunted=self.root.folder)

        ghost = self.root.target.ghost

        # Delete content. They are directly removed from the ghost
        # folder if they are ghosts.
        self.assertTrue('index' in ghost.objectIds())
        self.assertTrue('folder' in ghost.objectIds())
        self.assertTrue('publication' in ghost.objectIds())

        with IContainerManager(self.root.folder).deleter() as deleter:
            deleter(self.root.folder.index)
            deleter(self.root.folder.folder)

        self.assertFalse('index' in ghost.objectIds())
        self.assertFalse('folder' in ghost.objectIds())
        self.assertTrue('publication' in ghost.objectIds())

        # If you haunt again, nothing should change.
        ghost.haunt()
        self.assertFalse('index' in ghost.objectIds())
        self.assertFalse('folder' in ghost.objectIds())
        self.assertTrue('publication' in ghost.objectIds())

    def test_ghost_haunt_add_ghosts(self):
        """Test modifications: adding content in the target creates
        new ghosts in the ghost folder when the ghost folder is
        haunted.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder('ghost', None, haunted=self.root.folder)

        ghost = self.root.target.ghost

        # Add content. They are added when the ghost folder is haunted
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('testing', 'Testing')
        factory = self.root.folder.folder.manage_addProduct['Silva']
        factory.manage_addFolder('results', 'Testing results')

        self.assertFalse('testing' in ghost.objectIds())
        self.assertTrue('folder' in ghost.objectIds())
        self.assertFalse('results' in ghost.folder.objectIds())

        ghost.haunt()
        self.assertTrue('testing' in ghost.objectIds())
        self.assertTrue(verifyObject(IGhost, ghost.testing))
        self.assertTrue('folder' in ghost.objectIds())
        self.assertTrue('results' in ghost.folder.objectIds())
        self.assertTrue(verifyObject(IGhostFolder, ghost.folder.results))

    def test_ghost_haunt_add_assets(self):
        """Test modifications: adding assets in the target creates new
        assets in the ghost folder when the ghost folder is haunted.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder('ghost', None, haunted=self.root.folder)

        ghost = self.root.target.ghost
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addMockupAsset('data', 'Data set 1')
        factory = self.root.folder.publication.manage_addProduct['Silva']
        factory.manage_addMockupAsset('results', 'Results set 1')

        self.assertFalse('data' in ghost.objectIds())
        self.assertTrue('publication' in ghost.objectIds())
        self.assertFalse('results' in ghost.publication.objectIds())

        ghost.haunt()
        self.assertTrue('data' in ghost.objectIds())
        self.assertTrue(verifyObject(IMockupAsset, ghost.data))
        self.assertTrue('publication' in ghost.objectIds())
        self.assertTrue(verifyObject(IMockupAsset, ghost.publication.results))

    def test_ghost_haunt_remove_assets(self):
        """Test modifications: removing asssets in the target doesn't
        remove them automatically in the ghost folder, but this is
        done when the ghost folder is haunted.
        """
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addMockupAsset('data', 'Data set 1')
        factory.manage_addMockupAsset('export', 'Export set 1')
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder('ghost', None, haunted=self.root.folder)

        ghost = self.root.target.ghost
        with IContainerManager(self.root.folder).deleter() as deleter:
            deleter(self.root.folder.data)
            deleter(self.root.folder.export)

        self.assertTrue('data' in ghost.objectIds())
        self.assertTrue(verifyObject(IMockupAsset, ghost.data))
        self.assertTrue('export' in ghost.objectIds())
        self.assertTrue(verifyObject(IMockupAsset, ghost.export))

        ghost.haunt()
        self.assertFalse('data' in ghost.objectIds())
        self.assertFalse('export' in ghost.objectIds())

    def test_ghost_haunt_add_ghosts_for_ghosts(self):
        """Test modification: adding ghost to the target will create
        new ghosts in the ghost golder when it is haunted.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder('ghost', None, haunted=self.root.folder)

        ghost = self.root.target.ghost
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addGhost(
            'notes', None, haunted=self.root.folder.document)
        IPublicationWorkflow(self.root.folder.notes).publish()
        self.assertFalse('notes' in ghost.objectIds())

        ghost.haunt()
        self.assertTrue('notes' in ghost.objectIds())
        self.assertTrue(verifyObject(IGhost, ghost.notes))
        version = ghost.notes.get_editable()
        self.assertIs(version, None)
        version = ghost.notes.get_viewable()
        self.assertIsNot(version, None)
        self.assertEqual(version.get_haunted(), self.root.folder.document)
        self.assertEqual(version.get_link_status(), None)
        self.assertEqual(
            aq_chain(version.get_haunted()),
            aq_chain(self.root.folder.document))

    def test_ghost_haunt_remove_ghosts_for_ghosts(self):
        """Test modification: remove a target of a ghost that is
        ghosted by the ghost folder. The ghost (in the ghost folder)
        should be removed.
        """
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addGhost(
            'notes', None, haunted=self.root.folder.document)
        IPublicationWorkflow(self.root.folder.notes).publish()
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost', None, haunted=self.root.folder)

        ghost = self.root.target.ghost
        self.assertTrue('notes' in ghost.objectIds())
        self.assertTrue(verifyObject(IGhost, ghost.notes))
        version = ghost.notes.get_editable()
        self.assertIs(version, None)
        version = ghost.notes.get_viewable()
        self.assertIsNot(version, None)
        self.assertEqual(version.get_haunted(), self.root.folder.document)

        with IContainerManager(self.root.folder).deleter() as deleter:
            deleter(self.root.folder.document)

        self.assertTrue('notes' in self.root.folder.objectIds())
        self.assertEqual(self.root.folder.notes.get_haunted(), None)
        self.assertFalse('notes' in ghost.objectIds())

        # Nothing should change if the folder is ghosted (broken
        # ghosts should not be created).
        ghost.haunt()
        self.assertTrue('notes' in self.root.folder.objectIds())
        self.assertEqual(self.root.folder.notes.get_haunted(), None)
        self.assertFalse('notes' in ghost.objectIds())

    def test_ghost_haunt_remove_ghosted_content_for_ghosts(self):
        """Test modification: remove a target of a ghost that is
        ghosted by the ghost folder. The ghost (in the ghost folder)
        should be removed.
        """
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addGhost(
            'notes', None, haunted=self.root.folder.document)
        IPublicationWorkflow(self.root.folder.notes).publish()
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost', None, haunted=self.root.folder)

        ghost = self.root.target.ghost
        self.assertTrue('notes' in ghost.objectIds())
        self.assertTrue(verifyObject(IGhost, ghost.notes))
        version = ghost.notes.get_editable()
        self.assertIs(version, None)
        version = ghost.notes.get_viewable()
        self.assertIsNot(version, None)
        self.assertEqual(version.get_haunted(), self.root.folder.document)

        with IContainerManager(self.root.folder).deleter() as deleter:
            deleter(self.root.folder.notes)

        # The ghosted ghost is remove, and the ghost is not touched
        # (the document is still there).
        self.assertFalse('notes' in self.root.folder.objectIds())
        self.assertTrue('notes' in ghost.objectIds())
        self.assertTrue(verifyObject(IGhost, ghost.notes))
        version = ghost.notes.get_editable()
        self.assertIs(version, None)
        version = ghost.notes.get_viewable()
        self.assertIsNot(version, None)
        self.assertEqual(version.get_haunted(), self.root.folder.document)

        # Haunting should remove the ghost since it does no longer exists
        ghost.haunt()
        self.assertFalse('notes' in self.root.folder.objectIds())
        self.assertFalse('notes' in ghost.objectIds())

    def test_ghost_haunt_add_ghost_folders_for_ghost_folders(self):
        """Test modification: add a ghost folder in the target
        folder. When the ghost folder will be haunted, it will create
        a ghost folder with the same target as the ghosted ghost
        folder.
        """
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost', None, haunted=self.root.folder)

        ghost = self.root.target.ghost
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'backup', None, haunted=self.root.folder.publication)
        self.assertFalse('backup' in ghost.objectIds())

        ghost.haunt()
        self.assertTrue('backup' in ghost.objectIds())
        self.assertTrue(verifyObject(IGhostFolder, ghost.backup))
        self.assertEqual(ghost.backup.get_link_status(), None)
        self.assertEqual(
            ghost.backup.get_haunted(),
            self.root.folder.publication)
        self.assertEqual(
            aq_chain(ghost.backup.get_haunted()),
            aq_chain(self.root.folder.publication))
        # Content in this ghost folder have been ghosted
        self.assertTrue('document' in ghost.backup.objectIds())
        self.assertTrue(verifyObject(IGhost, ghost.backup.document))

    def test_ghost_haunt_remove_ghost_folders_for_ghost_folders(self):
        """Test modification: remove a target of a ghost folder from a
        folder that is the target of a ghost folder. The ghost folder
        corresponding to the first ghost folder should be removed from
        this later one.
        """
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'backup', None, haunted=self.root.folder.publication)
        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost', None, haunted=self.root.folder)

        ghost = self.root.target.ghost
        self.assertTrue('backup' in ghost.objectIds())
        self.assertTrue(verifyObject(IGhostFolder, ghost.backup))

        with IContainerManager(self.root.folder).deleter() as deleter:
            deleter(self.root.folder.publication)

        self.assertTrue('backup' in self.root.folder.objectIds())
        self.assertEqual(
            self.root.folder.backup.get_link_status(),
            errors.EmptyInvalidTarget())
        self.assertFalse('backup' in ghost.objectIds())

        # Ghosting should not change anything
        ghost.haunt()
        self.assertTrue('backup' in self.root.folder.objectIds())
        self.assertEqual(
            self.root.folder.backup.get_link_status(),
            errors.EmptyInvalidTarget())
        self.assertFalse('backup' in ghost.objectIds())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GhostFolderTestCase))
    return suite
