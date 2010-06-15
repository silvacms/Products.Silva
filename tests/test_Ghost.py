# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva import SilvaPermissions
from Products.Silva.Ghost import GhostVersion

from zope.interface.verify import verifyObject
from zope.i18n import translate

from Products.Silva.testing import FunctionalLayer
from Products.Silva.tests.helpers import resetPreview, \
    approveObject, publishObject, publishApprovedObject

from silva.core import interfaces as silvainterfaces
from silva.core.references.reference import BrokenReferenceError


class GhostTestCase(unittest.TestCase):
    """Test the Ghost object.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        def factory(obj, product="Silva"):
            return obj.manage_addProduct[product]

        for i in range(1,4):
            id = 'doc%d' % i
            title = 'Doc%d' % i
            factory(self.root, 'SilvaDocument').manage_addDocument(id, title)
            setattr(self, id, getattr(self.root, id))

        factory(self.root).manage_addFolder('folder4', 'Folder4')
        self.folder4 = folder4 = getattr(self.root, 'folder4')

        factory(self.root).\
            manage_addPublication('publication5', 'Publication5')
        self.publication5 = publication5 = getattr(self.root, 'publication5')

        factory(folder4, 'SilvaDocument').\
            manage_addDocument('subdoc', 'Subdoc')
        self.subdoc = subdoc = getattr(folder4, 'subdoc')

        factory(folder4).manage_addFolder('subfolder', 'Subfolder')
        self.subfolder = subfolder = getattr(folder4, 'subfolder')

        factory(subfolder, 'SilvaDocument').\
            manage_addDocument('subsubdoc', 'Subsubdoc')
        self.subsubdoc = subsubdoc = getattr(subfolder, 'subsubdoc')

        factory(publication5, 'SilvaDocument').\
            manage_addDocument('subdoc2', 'Subdoc2')
        self.subdoc2 = subdoc2 = getattr(publication5, 'subdoc2')

    def test_broken_link1(self):
        # add a ghost
        self.root.manage_addProduct['Silva'].manage_addGhost(
            'ghost1', 'Ghost1', haunted=self.root.doc1)
        ghost = getattr(self.root, 'ghost1')

        # issue 41: test if get_haunted_url works now
        self.assertEquals('/root/doc1', ghost.get_editable().get_haunted_url())
        self.assertEquals(None, ghost.get_editable().get_link_status())

        # now delete doc1
        def delete():
            self.root.action_delete(['doc1'])
        self.assertRaises(BrokenReferenceError, delete)

    def test_ghost_title(self):
        self.root.manage_addProduct['Silva'].manage_addGhost(
            'ghost1', 'Ghost 1', haunted=self.root.doc1)
        # need to publish doc1 first
        publishObject(self.root.doc1)
        ghost = getattr(self.root, 'ghost1')
        # FIXME: should we be able to get title of unpublished document?
        self.assertEquals('Doc1', ghost.get_title_editable())
        # now publish ghost
        publishObject(ghost)

        # should have title of whatever we're pointing at now
        self.assertEquals('Doc1', ghost.get_title())
        # now break link
        self.root.doc1.close_version()
        
        def delete():
            self.root.action_delete(['doc1'])
        self.assertRaises(BrokenReferenceError, delete)

    # FIXME: ghost should do read access checks, test for it somehow?

    def test_ghost_points(self):
        # test that the ghost cannot point to the wrong thing;
        # only non-ghost versioned content
        id = 'ghost1'
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost(id, 'Ghost')
        ghost = getattr(self.root, id)

        factory.manage_addImage('image6', 'Test image')
        image = getattr(self.root, 'image6')

        self.assertEquals(GhostVersion.LINK_EMPTY,
                          ghost.get_editable().get_link_status())
        ghost.get_editable().set_haunted(self.folder4)
        self.assertEquals(GhostVersion.LINK_FOLDER,
                          ghost.get_editable().get_link_status())
        ghost.get_editable().set_haunted(ghost)
        self.assertEquals(GhostVersion.LINK_GHOST,
                          ghost.get_editable().get_link_status())
        ghost.get_editable().set_haunted(image)
        self.assertEquals(GhostVersion.LINK_NO_CONTENT,
            ghost.get_editable().get_link_status())

    def test_ghostfolder(self):
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'gf1', 'GhostFolder', haunted=self.publication5)
        gfpub = getattr(self.root, 'gf1')

        factory.manage_addGhostFolder(
            'gf2', 'GhostFolder2', haunted=self.folder4)
        gffold = getattr(self.root, 'gf2')

        self.assertTrue(gfpub.implements_container())
        self.assertTrue(gfpub.implements_publication())
        self.assertTrue(not gffold.implements_publication())
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
        publishObject(doc)

        self.assertTrue(gfpub.is_published())

        # now if we close the haunted document, is_published() should return
        # false again
        ghostdoc = gfpub.subdoc2
        ghostdoc.close_version()

        self.assertTrue(not gfpub.is_published())


    def test_ghostfolder_topub(self):
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

    def test_circular_links(self):
        # add some content in a tree
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('f', 'F')
        f = getattr(self.root, 'f')

        factory = f.manage_addProduct['Silva']
        factory.manage_addFolder('g', 'G')
        g = getattr(f, 'g')

        factory = g.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('foo', 'Foo')
        doc = getattr(g, 'foo')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('h', 'H')
        h = getattr(self.root, 'h')

        factory.manage_addGhostFolder(
            'gf1', 'Ghost forlder 1', haunted=g)
        gf1 = getattr(self.root, 'gf1')

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


    def test_modification_time(self):
        # https://infrae.com/issue/silva/issue1645
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost(
            'ghost1', 'Ghost 1', haunted=self.doc1)
        ghost = getattr(self.root, 'ghost1')

        self.assertEqual(ghost.get_modification_datetime(),
                         self.doc1.get_modification_datetime())

        # Let's delete the haunted object;
        # `get_modification_datetime` should still work
        del ghost.getLastVersion()._haunted
        self.root.manage_delObjects(['doc1'])
        self.assertEqual(ghost.get_modification_datetime(), None)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GhostTestCase))
    return suite
