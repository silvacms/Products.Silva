# Copyright (c) 2003-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from DateTime import DateTime
from Products.Silva.adapters.tree import getTreeNodeAdapter

# from Products.Silva import Ghost

class TreeNodeTestCase(SilvaTestCase.SilvaTestCase):
                                                                                
    def afterSetUp(self):
        self.pub = pub = self.add_folder(
            self.root, 'pub', 'Publication')
        
        #self.toghost  = toghost = self.add_document(
        #    self.root, 'toghost', 'To be Haunted')
        self.gamma  = gamma = self.add_document(self.pub, 'gamma', 'Gamma')
        self.alpha = alpha = self.add_document(self.pub, 'alpha', 'Alpha')
        self.beta = beta = self.add_document(self.pub, 'beta', 'Beta')
        #self.ghost = ghost = self.add_ghost(
        #    self.pub, 'ghost', '/'.join(toghost.getPhysicalPath()))

        #self.foldertoghost = self.add_folder(
        #    self.root, 'foldertoghost', 'Folder to Ghost')
        #self.ghostfolder = ghostfolder = Ghost.ghostFactory(
        #    self.pub, 'ghostfolder', self.foldertoghost)
        #self.ghostfolder.haunt()

        #self.broken_ghost = broken_ghost = self.add_ghost(
        #    self.pub, 'broken_ghost', '/this/object/does/not/exist')

        # add a folder with an indexable index document
        self.subfolder = subfolder =  self.add_folder(
            self.pub, 'folder_with_index_doc', 
            'SubFolder', policy_name='Silva Document')

        self.kappa = kappa = self.add_document(self.subfolder, 'kappa', 'Kappa')

        # publish documents
        for doc in [gamma, alpha, beta, subfolder.index]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

        # create one unpublished document that should never show up in the
        # tree
        self.omega = omega = self.add_document(self.root, 'omega', 'Omega')

    def test_treenode(self):
        #    root/pub/
        #    root/pub/gamma
        #    root/pub/alpha
        #    root/pub/beta
        #    root/pub/folder_with_index_doc
        #    root/pub/fodler_with_index_doc/index
        #    root/omega (unpubl.)
        node = getTreeNodeAdapter(self.root)
        expected = [u'Publication', u'Gamma', u'Alpha', u'Beta', 
                    u'SubFolder', 'omega']

        actual = []
        # XXX: extreme naive test, work in progress
        for child in node.getChildNodes():
            actual.append(child.getObject().get_title())
            for subchild in child.getChildNodes():
                actual.append(subchild.getObject().get_title())
    
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TreeNodeTestCase, 'test'))
        return suite
 
