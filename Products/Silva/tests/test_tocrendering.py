# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $

# Python
import unittest

from Products.Silva.adapters.tocrendering import \
    getTOCRenderingAdapter
from Products.Silva.tests import SilvaTestCase

from DateTime import DateTime
now = DateTime()

class TOCRenderingTestCase(SilvaTestCase.SilvaTestCase):
    """tests for the toc rendering adapter"""
    
    def afterSetUp(self):
        self.add_folder(self.root, 'f', 'f')
        self.add_document(self.root.f, 'index', 'index')
        doc = self.root.f.index
        doc.set_unapproved_version_publication_datetime(now)
        doc.approve_version()
        self.add_document(self.root, 'doc', 'doc')
        doc = self.root.doc
        doc.set_unapproved_version_publication_datetime(now)
        doc.approve_version()

    def test_container_urls(self):
        """make sure generated urls to containers have a trailing slash"""
        ad = getTOCRenderingAdapter(self.root)
        result = ad.render_tree()
        #this folder should have a trailing slash
        self.assertTrue(result.find('"http://nohost/root/f/"')>-1)
        #no double-slash
        self.assertTrue(result.find('"http://nohost/root/f//"')==-1)
        #a document does not have a trailing slash
        self.assertTrue(result.find('"http://nohost/root/doc"')>-1)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TOCRenderingTestCase))
    return suite
