# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase

import time
from DateTime import DateTime
from Products.Silva.SilvaObject import SilvaObject
from Products.SilvaDocument.Document import Document, DocumentVersion

SECOND = 1.0 / (24 * 60 * 60)

class ViewCacheTestCase(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.add_document(self.root, 'document', 'Document')
        self.document = self.root.document
    
    def beforeTearDown(self):
        pass
    
    def test_notPublished(self):
        doc = self.document
        # not publisehd
        self.assertEquals(
            "Sorry, this document is not published yet.", doc.view())
        self.assert_(not doc.is_cached())
          
    def test_published(self):
        # doc gets published, use cache
        doc = self.document
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        doc.view()
        self.assert_(doc.is_cached())
            
    def test_notCacheable(self):        
        # doc not cacheable
        doc = self.document
        dom = doc.get_editable().content
        dom.documentElement.appendChild(dom.createElement('toc'))
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        doc.view()
        self.assert_(not doc.is_cached())

    def test_republish(self):
        # new publication of doc, cache is invalid
        doc = self.document
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        doc.view()
        doc.close_version()
        doc.create_copy()
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        self.assert_(not doc.is_cached())
        doc.view()
        self.assert_(doc.is_cached())
        
    def test_closed(self):
        # idem for closed
        doc = self.document
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        doc.view()
        doc.close_version()
        self.assert_(not doc.is_cached())        
        
    def test_globalRefresh(self):
        # refreshtime is set, cache is invalid            
        doc = self.document
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        data = doc.view()
        self.assert_(doc.is_cached())
        self.root.service_extensions.refresh_caches()
        self.assert_(not doc.is_cached())
        self.assertEquals(data, doc.view())
        self.assert_(doc.is_cached())

    def test_nowIsCacheable(self):
        # publication was not cacheable, but new version is
        doc = self.document
        dom = doc.get_editable().content
        dom.documentElement.appendChild(dom.createElement('toc'))
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        data = doc.view()
        self.assert_(not doc.is_cached())
        doc.create_copy()
        dom = doc.get_editable().content
        dom.documentElement.removeChild(dom.documentElement.firstChild)        
        dom.documentElement.appendChild(dom.createElement('p'))        
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        self.assertNotEquals(data, doc.view())
        self.assert_(doc.is_cached())
    
    def test_nowIsNotCacheable(self):
        # publication was cacheable, but new version is not
        doc = self.document
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        data = doc.view()
        self.assert_(doc.is_cached())
        doc.create_copy()
        dom = doc.get_editable().content
        dom.documentElement.appendChild(dom.createElement('toc'))
        now = DateTime()
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        self.assertNotEquals(data, doc.view())
        self.assert_(not doc.is_cached())
        
    def test_publishInFuture(self):
        doc = self.document
        # publish a doc
        now = DateTime()
        dom1 = doc.get_editable().content        
        dom1.documentElement.appendChild(dom1.createElement('p'))
        doc.set_unapproved_version_publication_datetime(now - 1)
        doc.approve_version()
        data = doc.view()
        # create copy and edit
        now = DateTime()
        doc.create_copy()
        dom2 = doc.get_editable().content
        dom2.documentElement.appendChild(dom2.createElement('heading'))
        doc.set_unapproved_version_publication_datetime(now + SECOND/5.0)
        doc.approve_version()        
        self.assert_(doc.is_cached())
        self.assertEquals(data, doc.view())
        #time.sleep(SECOND)
        #self.assert_(not doc.is_cached())
        #self.assertNotEquals(data, doc.view())
        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(ViewCacheTestCase))
        return suite
    