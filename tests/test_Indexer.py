# Copyright (c) 2003-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase

from DateTime import DateTime

class IndexerTestCase(SilvaTestCase.SilvaTestCase):
                                                                                
    def afterSetUp(self):
        self.pub = pub = self.add_folder(
            self.root, 'pub', 'Publication')
        
        self.gamma  = gamma = self.add_document(self.root, 'gamma', 'Gamma')
        self.alpha = alpha = self.add_document(self.root, 'alpha', 'Alpha')
        self.beta = beta = self.add_document(self.root, 'beta', 'Beta')
        self.kappa = kappa = self.add_document(self.root, 'kappa', 'Kappa')

        getattr(gamma, '0').content.manage_edit(
            '<doc>'
            '<p>Foo bar <index name="a" /></p>'
            '<p>Baz <index name="b" /></p>'
            '</doc>')
        getattr(alpha, '0').content.manage_edit(
            '<doc>'
            '<p>Hey <index name="a" /></p>'
            '</doc>')
        getattr(beta, '0').content.manage_edit(
            '<doc>'
            '<p>Hello <index name="b" /></p>'
            '</doc>')
        getattr(kappa, '0').content.manage_edit(
            '<doc>'
            '<p>Dag <index name="c" /></p>'
            '</doc>')

        # publish documents
        for doc in [gamma, alpha, beta, kappa]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

        # create one unpublished document that should never show up in the
        # index
        self.omega = omega = self.add_document(self.root, 'omega', 'Omega')

        getattr(gamma, '0').content.manage_edit(
            '<doc>'
            '<p>hello hello <index name="d" /></p>'
            '</doc>')

        # now create the indexer itself
        self.root.pub.manage_addProduct['Silva'].manage_addIndexer(
            'indexer', 'Title')
        self.indexer = self.pub.indexer
        
    def test_indexer(self):
        self.indexer.update_index()
        
    
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(IndexerTestCase, 'test'))
        return suite
 
