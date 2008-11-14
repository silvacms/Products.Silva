# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision$
import SilvaTestCase

from DateTime import DateTime
from Products.Silva import Ghost
from Products.Silva.interfaces import IHaunted

class HauntedTestCase(SilvaTestCase.SilvaTestCase):
    """Test the Haunted adapter.
    """
    def afterSetUp(self):
        """Content tree:
        
        /doc1
        /publication
        /publication/folder
        /publication/folder/doc2
        /ghost
        /link
        
        """
        self.doc1 = self.add_document(self.root, 'doc1', u'Test Document 1')
        self.publication = self.add_publication(self.root, 'publication', u'Test Publication')
        self.folder = self.add_folder(self.publication, 'folder', u'Test Folder')
        self.ghost = self.add_ghost(self.root, 'ghost', 'somesortofcontenturl')
        self.link = self.add_link(self.root, 'link', u'Test Link', 'url')

    def test_getHaunting(self):
        # No adapter for non-content or containers objects
        self.assertRaises(TypeError, IHaunted, self.root.service_catalog)
        self.assertRaises(TypeError, IHaunted, self.publication)
        self.assertRaises(TypeError, IHaunted, self.folder)
        # Test getting an adapter for content
        adapted = IHaunted(self.doc1)
        self.assert_(adapted)
        adapted = IHaunted(self.link)
        self.assert_(adapted)
        adapted = IHaunted(self.ghost)
        self.assert_(adapted)
        # Create a ghost of the doc the haunting list for this object
        ghostofdoc = Ghost.ghostFactory(self.root, 'ghostofdoc', self.doc1)
        self.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc1.approve_version()
        ghostofdoc.set_unapproved_version_publication_datetime(DateTime() - 1)
        ghostofdoc.approve_version()
        # See if it works :)
        adapted = IHaunted(self.doc1)
        thehaunting = adapted.getHaunting()
        ghost = thehaunting.next()
        self.assertEquals(ghostofdoc.getPhysicalPath(), ghost.getPhysicalPath())
        # There should be only one
        self.assertRaises(StopIteration, thehaunting.next)
        
def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HauntedTestCase))
    return suite
