7# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase

from DateTime import DateTime

from Products.Silva import Ghost

from Products.Silva.adapters import haunted

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
        notadapted = haunted.getHaunted(self.root.service_catalog)
        self.assertEquals(notadapted, None)
        notadapted = haunted.getHaunted(self.publication)
        self.assertEquals(notadapted, None)
        notadapted = haunted.getHaunted(self.folder)
        self.assertEquals(notadapted, None)
        # Test getting an adapter for content
        adapted = haunted.getHaunted(self.doc1)
        self.assert_(adapted)
        adapted = haunted.getHaunted(self.link)
        self.assert_(adapted)
        adapted = haunted.getHaunted(self.ghost)
        self.assert_(adapted)
        # Create a ghost of the doc the haunting list for this object
        ghostofdoc = Ghost.ghostFactory(self.root, 'ghostofdoc', self.doc1)
        self.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc1.approve_version()
        ghostofdoc.set_unapproved_version_publication_datetime(DateTime() - 1)
        ghostofdoc.approve_version()
        # See if it works :)
        adapted = haunted.getHaunted(self.doc1)
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

if __name__ == '__main__':
    framework()
