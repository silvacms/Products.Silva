# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import SilvaTestCase

from Products.Silva import SilvaPermissions
from Products.Silva.Ghost import GhostVersion

from zope.interface.verify import verifyObject
from zope.i18n import translate

from Products.Silva.tests.helpers import resetPreview, \
    approveObject, publishObject, publishApprovedObject

from silva.core import interfaces as silvainterfaces


class GhostTestCase(SilvaTestCase.SilvaTestCase):
    """Test the Ghost object.
    """
    def afterSetUp(self):

        # register silva document
        self.setPermissions([SilvaPermissions.ReadSilvaContent])
        self.doc1 = doc1 = self.add_document(self.root, 'doc1', 'Doc1')
        self.doc2 = doc2 = self.add_document(self.root, 'doc2', 'Doc2')
        self.doc3 = doc3 = self.add_document(self.root, 'doc3', 'Doc3')
        self.folder4 = folder4 = self.add_folder(self.root,
                  'folder4', 'Folder4')
        self.publication5 = publication5 = self.add_publication(self.root,
                  'publication5', 'Publication5')
        self.subdoc = subdoc = self.add_document(folder4,
                  'subdoc', 'Subdoc')
        self.subfolder = subfolder = self.add_folder(folder4,
                  'subfolder', 'Subfolder')
        self.subsubdoc = subsubdoc = self.add_document(subfolder,
                   'subsubdoc', 'Subsubdoc')
        self.subdoc2 = subdoc2 = self.add_document(publication5,
                   'subdoc2', 'Subdoc2')

    def test_ghost(self):
        self.add_ghost(self.root, 'ghost1', '/root/doc1')

        # testing call cases of published (1) and non published (0)

        ghost = getattr(self.root, 'ghost1')
        # there is no version published at all there
        # ghost=0, doc=0
        self.assertEquals('This ghost is broken. (/root/doc1)',
            translate(ghost.preview()))
        resetPreview(ghost)
        self.assertEquals('<p>Sorry', ghost.view()[:8])


        # approve version of thing we point to
        approveObject(self.doc1)

        # since there is still no published version, preview and view
        # return None ghost=0, doc=0
        self.assertEquals('This ghost is broken. (/root/doc1)',
            translate(ghost.preview()))
        resetPreview(ghost)
        self.assertEquals('<p>Sorry', ghost.view()[:8])

        # this should publish doc1
        publishApprovedObject(self.doc1)

        # ghost=0, doc=1
        self.assertEquals(u'<h2 class="heading">Doc1</h2>\n\n',
                          ghost.preview())
        resetPreview(ghost)
        self.assertEquals('<p>Sorry', ghost.view()[:8])

        # publish ghost version
        publishObject(ghost)

        # ghost=1, doc=1
        self.assertEquals(u'<h2 class="heading">Doc1</h2>\n\n',
                          ghost.preview())
        resetPreview(ghost)
        self.assertEquals(u'<h2 class="heading">Doc1</h2>\n\n',
                          ghost.view())

        # make new version of doc1 ('1')
        self.doc1.create_copy()
        self.doc1.set_title('Doc1 1')

        # the preview got the new version, but the published stay the same.
        self.assertEquals(u'<h2 class="heading">Doc1 1</h2>\n\n',
                          ghost.preview())
        resetPreview(ghost)
        self.assertEquals(u'<h2 class="heading">Doc1</h2>\n\n',
                          ghost.view())

        publishObject(self.doc1)

        # now we're ghosting the version 1
        self.assertEquals(u'<h2 class="heading">Doc1 1</h2>\n\n',
                          ghost.preview())
        resetPreview(ghost)
        self.assertEquals(u'<h2 class="heading">Doc1 1</h2>\n\n',
                          ghost.view())

        # since both the ghost and the doc are published, is_published()
        # should return true
        self.assert_(ghost.is_published())

        # create new version of ghost
        ghost.create_copy()
        ghost.get_editable().set_haunted_url('/root/doc2')

        self.assertEquals(u'This ghost is broken. (/root/doc2)',
                          translate(ghost.preview()))
        resetPreview(ghost)
        self.assertEquals(u'<h2 class="heading">Doc1 1</h2>\n\n',
                          ghost.view())

        # publish doc2
        publishObject(self.doc2)

        self.assertEquals(u'<h2 class="heading">Doc2</h2>\n\n',
                          ghost.preview())
        resetPreview(ghost)
        self.assertEquals(u'<h2 class="heading">Doc1 1</h2>\n\n',
                          ghost.view())


        # approve ghost again
        publishObject(ghost)

        self.assertEquals(u'<h2 class="heading">Doc2</h2>\n\n',
                          ghost.preview())
        resetPreview(ghost)
        self.assertEquals(u'<h2 class="heading">Doc2</h2>\n\n',
                          ghost.view())

        # publish a ghost pointing to something that hasn't a published
        # version
        ghost.create_copy()
        ghost.get_editable().set_haunted_url('/root/doc3')
        publishObject(ghost)
        self.assertEquals('This ghost is broken. (/root/doc3)',
                          translate(ghost.preview()))
        resetPreview(ghost)
        self.assertEquals("This 'ghost' document is broken. Please inform the"
            " site administrator.", translate(ghost.view()))

        # since the version isn't published is_published() should return
        # false
        self.assert_(not ghost.is_published())

    def test_broken_link1(self):
        # add a ghost
        self.root.manage_addProduct['Silva'].manage_addGhost('ghost1',
                                                              '/root/doc1/')
        ghost = getattr(self.root, 'ghost1')

        # issue 41: test if get_haunted_url works now
        self.assertEquals('/root/doc1', ghost.get_editable().get_haunted_url())
        self.assertEquals(None, ghost.get_editable().get_link_status())

        # now delete doc1
        self.root.action_delete(['doc1'])
        # ghost should say 'This ghost is broken'
        self.assertEquals('This ghost is broken. (/root/doc1)',
                          translate(ghost.preview()))
        resetPreview(ghost)
        # issue 41: test get_haunted_url; should catch KeyError
        # and return original inserted url
        self.assertEquals('/root/doc1',
                          ghost.get_previewable().get_haunted_url())
        self.assertEqual(GhostVersion.LINK_VOID,
                         ghost.get_editable().get_link_status())

        # now make ghost point to doc2, and publish ghost and doc2
        publishObject(self.doc2)
        ghost.create_copy()
        ghost.get_editable().set_haunted_url('/root/doc2')
        publishObject(ghost)

        # now close & delete doc2
        self.doc2.close_version()
        self.root.action_delete(['doc2'])
        self.assertEquals("This 'ghost' document is broken. Please inform the site administrator.",
                          translate(ghost.view()))
        # issue 41: test get_haunted_url; should catch KeyError
        # and return original inserted url
        self.assertEquals('/root/doc2',
                          ghost.get_previewable().get_haunted_url())
        self.assertEquals(GhostVersion.LINK_VOID,
                          ghost.get_previewable().get_link_status())


    def test_ghost_title(self):
        self.root.manage_addProduct['Silva'].manage_addGhost('ghost1',
                                                              '/root/doc1')
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
        self.root.action_delete(['doc1'])
        self.assertEquals('Ghost target is broken',
                          ghost.get_title())

    # FIXME: ghost should do read access checks, test for it somehow?

    def test_ghost_points(self):
        # test that the ghost cannot point to the wrong thing;
        # only non-ghost versioned content
        ghost = self.add_ghost(self.root, 'ghost1', '/root/does_not_exist')
        self.add_image(self.root, 'image6', 'Test image')

        self.assertEquals('This ghost is broken. (/root/does_not_exist)',
                          translate(ghost.preview()))
        resetPreview(ghost)
        self.assertEquals(GhostVersion.LINK_VOID,
                          ghost.get_editable().get_link_status())
        ghost.get_editable().set_haunted_url('/root/folder4')
        self.assertEquals('This ghost is broken. (/root/folder4)',
                          translate(ghost.preview()))
        resetPreview(ghost)
        self.assertEquals(GhostVersion.LINK_FOLDER,
                          ghost.get_editable().get_link_status())
        ghost.get_editable().set_haunted_url('/root/ghost1')
        self.assertEquals('This ghost is broken. (/root/ghost1)',
                          translate(ghost.preview()))
        resetPreview(ghost)
        self.assertEquals(GhostVersion.LINK_GHOST,
                          ghost.get_editable().get_link_status())
        ghost.get_editable().set_haunted_url('/root/image6')
        self.assertEquals('This ghost is broken. (/root/image6)',
                          translate(ghost.preview()))
        resetPreview(ghost)
        self.assertEquals(GhostVersion.LINK_NO_CONTENT,
            ghost.get_editable().get_link_status())

    def test_ghostfolder(self):
        gfpub = self.addObject(self.root, 'GhostFolder', 'gf1',
                               content_url='/root/publication5')
        gffold = self.addObject(self.root, 'GhostFolder', 'gf2',
                                content_url='/root/folder4')
        self.assert_(gfpub.implements_container())
        self.assert_(gfpub.implements_publication())
        self.assert_(not gffold.implements_publication())
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
        self.assert_(not gfpub.is_published())

        # the ghost's documents are published on creation, so if we publish
        # the haunted document is_published() should return true
        doc = self.subdoc2
        publishObject(doc)

        self.assert_(gfpub.is_published())

        # now if we close the haunted document, is_published() should return
        # false again
        ghostdoc = gfpub.subdoc2
        ghostdoc.close_version()

        self.assert_(not gfpub.is_published())


    def test_ghostfolder_topub(self):
        gfpub = self.addObject(self.root, 'GhostFolder', 'gf1',
                               content_url='/root/publication5')
        self.assert_(gfpub.implements_container())
        self.assert_(gfpub.implements_publication())
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
        self.add_folder(self.root, 'f', 'F')
        f = self.root.f
        self.add_folder(f, 'g', 'G')
        g = self.root.f.g
        self.add_document(g, 'foo', 'Foo')
        doc = g.foo
        self.add_folder(self.root, 'h', 'H')
        # add a non-circular ghost folder
        self.root.manage_addProduct['Silva'].manage_addGhostFolder(
            'gf1',
            '/root/f/g')
        self.assertEquals('/root/f/g',
                          self.root.gf1.get_haunted_url())
        self.assertEquals(self.root.gf1.LINK_OK,
                          self.root.gf1.get_link_status())
        # now change link to circular
        self.root.gf1.set_haunted_url('/root')
        self.assertEquals(self.root.gf1.LINK_CIRC,
                          self.root.gf1.get_link_status())
        # set up some more complicated circular setup
        g.manage_addProduct['Silva'].manage_addGhostFolder(
            'gf2',
            '/root/f/g')
        gf2 = g.gf2
        self.assertEquals(
            gf2.LINK_CIRC,
            gf2.get_link_status())
        gf2.set_haunted_url('/root/f/g/gf2')
        self.assertEquals(
            gf2.LINK_GHOST,
            gf2.get_link_status())
        gf2.set_haunted_url('/root/f/g')
        self.assertEquals(
            gf2.LINK_CIRC,
            gf2.get_link_status())
        gf2.set_haunted_url('/root')
        self.assertEquals(
            gf2.LINK_CIRC,
            gf2.get_link_status())
        gf2.set_haunted_url('/root/h')
        self.assertEquals(
            gf2.LINK_OK,
            gf2.get_link_status())

        #self.assertEquals('/root/doc1', ghost.get_editable().get_haunted_url())
        #self.assertEquals(None, ghost.get_editable().get_link_status())

    def test_modification_time(self):
        # https://infrae.com/issue/silva/issue1645
        self.add_ghost(self.root, 'ghost1', '/root/doc1')
        ghost = self.root.ghost1
        self.assertEqual(ghost.get_modification_datetime(),
                         self.doc1.get_modification_datetime())

        # Let's delete the haunted object;
        # `get_modification_datetime` should still work
        self.root.manage_delObjects(['doc1'])
        self.assertEqual(ghost.get_modification_datetime(), None)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GhostTestCase))
    return suite
