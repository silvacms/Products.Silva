# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from silva.core.interfaces import IHaunted

from Products.Silva.testing import FunctionalLayer
from Products.Silva.tests.helpers import publish_object
from Products.Silva.Ghost import ghost_factory


class HauntedTestCase(unittest.TestCase):
    """Test the Haunted adapter.
    """
    layer = FunctionalLayer

    def setUp(self):
        """Content tree:

        /doc1
        /publication
        /publication/folder
        /publication/folder/doc2
        /ghost
        /link

        """
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('doc', u'Test Document 1')
        self.doc = getattr(self.root, 'doc')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', u'Test Publication')
        self.publication = getattr(self.root, 'publication')
        factory.manage_addGhost('ghost', None, haunted=self.doc)
        self.ghost = getattr(self.root, 'ghost')
        factory.manage_addLink('link', u'Test Link')
        self.link = getattr(self.root, 'link')
        factory = self.publication.manage_addProduct['Silva']
        factory.manage_addFolder('folder', u'Test Folder')
        self.folder = getattr(self.publication, 'folder')


    def test_get_haunting(self):
        # No adapter for non-content or containers objects
        self.assertRaises(TypeError, IHaunted, self.root.service_catalog)
        self.assertRaises(TypeError, IHaunted, self.publication)
        self.assertRaises(TypeError, IHaunted, self.folder)

        # Test getting an adapter for content
        self.failUnless(verifyObject(
                IHaunted, IHaunted(self.doc)))
        self.failUnless(verifyObject(
                IHaunted, IHaunted(self.link)))
        self.failUnless(verifyObject(
                IHaunted, IHaunted(self.ghost)))

        # Create a ghost of the doc the haunting list for this object
        ghostofdoc = ghost_factory(self.root, 'ghostofdoc', self.doc)
        publish_object(ghostofdoc)
        publish_object(self.doc)

        # See if it works :)
        adapted = IHaunted(self.doc)
        thehaunting = adapted.getHaunting()

        ghost = thehaunting.next()
        self.assertEquals(
            ghostofdoc.getPhysicalPath(),
            ghost.getPhysicalPath())

        # There should be only one
        self.assertRaises(StopIteration, thehaunting.next)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HauntedTestCase))
    return suite
