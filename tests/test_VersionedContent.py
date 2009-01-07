# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.22 $
import SilvaTestCase

import time
from DateTime import DateTime
from Products.SilvaDocument.Document import Document, DocumentVersion
from Products.Silva.SilvaObject import SilvaObject

# monkey patch for the SilvaObject.view
not_viewable='Sorry, this document is not published yet.'
viewable='viewable'
def base_view(self):
    if self.get_viewable():
        return viewable
    else:
        return not_viewable

# backup of some methods to avoid interferences with other tests
orig_view = SilvaObject.view
orig_is_cacheable = Document.is_cacheable

class VersionedContentTestCase(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.document = self.add_document(self.root, 'document', 'Document')

        # monkey patches for the test_cache
        SilvaObject.view = base_view
        Document.is_cacheable = lambda x: 1
    
    def beforeTearDown(self):
        SilvaObject.view = orig_view
        Document.is_cacheable = orig_is_cacheable
    
    def test_workflow1(self):
        document = self.document
        self.assertEquals(document.get_editable().id, '0')
        self.assertEquals(document.get_previewable().id, '0')
        self.assertEquals(document.get_viewable(), None)
        # set publication datetime in the future
        document.set_unapproved_version_publication_datetime(DateTime() + 1)
        # approve version 
        document.approve_version()
        self.assertEquals(document.get_editable(), None)
        self.assertEquals(document.get_previewable().id, '0')
        self.assertEquals(document.get_viewable(), None)
        # now change publication datetime to something in the past, so
        # publication will happen
        document.set_approved_version_publication_datetime(DateTime() - 1)
        self.assertEquals(document.get_editable(), None)
        self.assertEquals(document.get_previewable().id, '0')
        self.assertEquals(document.get_viewable().id, '0')
        # now create a copy of the public version
        document.create_copy()
        self.assertEquals(document.get_editable().id, '1')
        self.assertEquals(document.get_previewable().id, '1')
        self.assertEquals(document.get_viewable().id, '0')

    def test_workflow2(self):
        document = self.document
        self.assertEquals(document.get_editable().id, '0')
        self.assertEquals(document.get_previewable().id, '0')
        self.assertEquals(document.get_viewable(), None)
        # set publication datetime in the past to ensure instant publication
        document.set_unapproved_version_publication_datetime(DateTime() - 1)
        # also instant expiration
        document.set_unapproved_version_expiration_datetime(DateTime() - .5)
        # approve version so will be published & expired at once
        document.approve_version()
        self.assertEquals(document.get_editable(), None)
        # we will show last closed version as preview in this case
        self.assertEquals(document.get_previewable().id, '0')
        self.assertEquals(document.get_viewable(), None)
        # now create a copy of the last closed version
        document.create_copy()
        self.assertEquals(document.get_editable().id, '1')
        self.assertEquals(document.get_previewable().id, '1')
        self.assertEquals(document.get_viewable(), None)

    def test_workflow3(self):
        document = self.document
        self.assertEquals(document.get_editable().id, '0')
        self.assertEquals(document.get_previewable().id, '0')
        self.assertEquals(document.get_viewable(), None)
        # set publication datetime in the past to ensure instant publication
        document.set_unapproved_version_publication_datetime(DateTime() - 1)
        # no expiration though
        # approve version so will be published at once
        document.approve_version()
        # instantly close version
        document.close_version()
        self.assertEquals(document.get_editable(), None)
        self.assertEquals(document.get_previewable().id, '0')
        self.assertEquals(document.get_viewable(), None)
        # now create a copy of the last closed version
        document.create_copy()
        self.assertEquals(document.get_editable().id, '1')
        self.assertEquals(document.get_previewable().id, '1')
        self.assertEquals(document.get_viewable(), None)

    def test_cache(self):
        # XXX for some reason this test fails, which is scary
        
        # cacheability of the test document is actually 
        # not part of the test, but a necessary preliminary
        self.assert_(self.document.is_cacheable())
        
        self.assertEquals(not_viewable, self.document.view())
        # the second call should come from the cache (can this be tested?)
        self.assertEquals(not_viewable, self.document.view())
        self.document.set_unapproved_version_publication_datetime(DateTime()-1)
        self.document.approve_version()
        self.assertEquals(viewable, self.document.view())
        self.assertEquals(viewable, self.document.view())

        # wait one tick more until closing
        time.sleep(0.1)
        
        self.document.close_version()
        self.assertEquals(None, self.document.get_public_version())
        self.assertEquals(not_viewable, self.document.view())
        self.assertEquals(not_viewable, self.document.view())

        self.document.create_copy()
        self.assertEquals(not_viewable, self.document.view())

        self.document.set_unapproved_version_publication_datetime(DateTime()-1)
        time.sleep(0.1)
        # expire after 1 second .... ugly, may fail on slow computers
        self.document.set_unapproved_version_expiration_datetime(DateTime()+1.0/(3600.0*24.0))
        date = self.document.get_unapproved_version_expiration_datetime()
        self.document.approve_version()
        self.assertEquals(viewable, self.document.view())
        self.assertEquals(viewable, self.document.view())

        # print 'waiting for expiry ...'
        time.sleep(1.5)

        self.assertEquals(not_viewable, self.document.view())
        self.assertEquals(not_viewable, self.document.view())
        
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersionedContentTestCase))
    return suite
