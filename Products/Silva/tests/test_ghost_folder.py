# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from zope.component import getUtility

from DateTime import DateTime
from Acquisition import aq_chain

from Products.Silva.testing import FunctionalLayer
from Products.Silva.tests.helpers import publish_object

from silva.core.interfaces import IGhostFolder
from silva.core.interfaces import IContainerManager, IPublicationWorkflow
from silva.core.references.reference import BrokenReferenceError
from silva.core.references.interfaces import IReferenceService, IReferenceValue


class GhostTestCase(unittest.TestCase):
    """Test the Ghost object.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addPublication('publication', 'Publication')

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('ghost', 'Ghost')
        return

        def factory(obj, product="Silva"):
            return obj.manage_addProduct[product]

        for i in range(1,4):
            id = 'doc%d' % i
            title = 'Doc%d' % i
            factory(self.root, 'SilvaDocument').manage_addDocument(id, title)
            setattr(self, id, getattr(self.root, id))

        factory(self.root).\
            manage_addPublication('publication5', 'Publication5')
        self.publication5 = getattr(self.root, 'publication5')

        factory(self.folder4, 'SilvaDocument').\
            manage_addDocument('subdoc', 'Subdoc')
        self.subdoc = getattr(self.folder4, 'subdoc')

        factory(self.folder4).manage_addFolder('subfolder', 'Subfolder')
        self.subfolder = getattr(self.folder4, 'subfolder')

        factory(self.subfolder, 'SilvaDocument').\
            manage_addDocument('subsubdoc', 'Subsubdoc')
        self.subsubdoc = getattr(self.subfolder, 'subsubdoc')

        factory(self.publication5, 'SilvaDocument').\
            manage_addDocument('subdoc2', 'Subdoc2')
        self.subdoc2 = getattr(self.publication5, 'subdoc2')

    def test_ghost_folder(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'gf1', 'GhostFolder', haunted=self.publication5)
        gfpub = getattr(self.root, 'gf1')

        factory.manage_addGhostFolder(
            'gf2', 'GhostFolder2', haunted=self.folder4)
        gffold = getattr(self.root, 'gf2')

        self.assertEquals(gfpub.get_link_status(), gfpub.LINK_OK)
        self.assertEquals(gffold.get_link_status(), gffold.LINK_OK)

        metadata_pub = self.root.service_metadata.getMetadata(
            self.root.publication5)
        metadata_gf = self.root.service_metadata.getMetadata(gfpub)
        metadata_pub.setValues('silva-content', {'maintitle': 'snafu'})
        self.assertEquals(metadata_gf.get('silva-content', 'maintitle'),
            'snafu')

        gfpub.haunt()

        # the publication's 'subdoc2' document is not published, so the ghost
        # folder should say it's not published either no matter what the
        # status of the contained ghost that points to the doc
        self.assertTrue(not gfpub.is_published())

        # the ghost's documents are published on creation, so if we publish
        # the haunted document is_published() should return true
        doc = self.subdoc2
        publish_object(doc)

        self.assertTrue(gfpub.is_published())

        # now if we close the haunted document, is_published() should return
        # false again
        ghostdoc = gfpub.subdoc2
        ghostdoc.close_version()

        self.assertTrue(not gfpub.is_published())

    def test_ghost_folder_to_publication(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'gf1', 'GhostFolder', haunted=self.publication5)
        gfpub = getattr(self.root, 'gf1')

        self.assertTrue(gfpub.implements_container())
        self.assertTrue(gfpub.implements_publication())
        self.assertEquals(gfpub.get_link_status(), gfpub.LINK_OK)
        metadata_pub = self.root.service_metadata.getMetadata(
            self.root.publication5)
        metadata_pub.setValues('silva-content', {'maintitle': 'snafu'})
        gfpub.to_publication()
        pub = self.root.gf1
        self.assertEquals(pub.meta_type, 'Silva Publication')
        metadata_newpub = self.root.service_metadata.getMetadata(pub)
        self.assertEquals(metadata_newpub.get('silva-content', 'maintitle'),
            'snafu')

    def test_ghost_folder_circular(self):
        # add some content in a tree
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('f', 'F')
        f = getattr(self.root, 'f')

        factory = f.manage_addProduct['Silva']
        factory.manage_addFolder('g', 'G')
        g = getattr(f, 'g')

        factory = g.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('foo', 'Foo')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('h', 'H')
        h = getattr(self.root, 'h')

        factory.manage_addGhostFolder(
            'gf1', 'Ghost forlder 1', haunted=g)

        self.assertEquals(g, self.root.gf1.get_haunted())
        self.assertEquals(self.root.gf1.LINK_OK,
                          self.root.gf1.get_link_status())

        # now change link to circular
        self.root.gf1.set_haunted(self.root)
        self.assertEquals(self.root.gf1.LINK_CIRC,
                          self.root.gf1.get_link_status())

        # set up some more complicated circular setup
        factory = g.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'gf2', 'Ghost folder2', haunted=g)
        gf2 = getattr(g, 'gf2')

        self.assertEquals(
            gf2.LINK_CIRC,
            gf2.get_link_status())
        gf2.set_haunted(gf2)
        self.assertEquals(
            gf2.LINK_GHOST,
            gf2.get_link_status())
        gf2.set_haunted(g)
        self.assertEquals(
            gf2.LINK_CIRC,
            gf2.get_link_status())
        gf2.set_haunted(self.root)
        self.assertEquals(
            gf2.LINK_CIRC,
            gf2.get_link_status())
        gf2.set_haunted(h)
        self.assertEquals(
            gf2.LINK_OK,
            gf2.get_link_status())

    def test_ghost_folder_modification_time(self):
        # https://infrae.com/issue/silva/issue1645
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost(
            'ghost1', 'Ghost 1', haunted=self.doc1)
        ghost = getattr(self.root, 'ghost1')

        self.assertEqual(
            ghost.get_modification_datetime(),
            self.doc1.get_modification_datetime())

        # Let's delete the haunted object;
        # `get_modification_datetime` should still work
        service = getUtility(IReferenceService)
        service.delete_reference(ghost.get_editable(), name=u'haunted')
        self.root.manage_delObjects(['doc1'])
        self.assertEqual(ghost.get_modification_datetime(), None)

    def test_ghost_folder_sync_twice(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghostfolder', 'Ghost Folder', haunted=self.folder4)
        ghostfolder = self.root.ghostfolder
        ghostfolder.haunt()
        ghost = ghostfolder.subdoc
        self.assertEquals('Silva Ghost', ghost.meta_type)
        ghost_version = ghost.get_viewable()
        self.assertEquals(self.subdoc, ghost_version.get_haunted())
        self.assertEquals('public',
                          ghost_version.version_status())
        self.subdoc.set_unapproved_version_publication_datetime(
            DateTime() - 10)
        self.subdoc.approve_version()
        ghostfolder.haunt()
        ghost_version2 = ghost.get_viewable()
        self.assertEquals(ghost_version, ghost_version2)
        self.assertEquals('public', ghost_version.version_status())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GhostTestCase))
    return suite
