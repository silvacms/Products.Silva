# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.6 $
import unittest
import Zope
from DateTime import DateTime
from Testing import makerequest
from Products.Silva.Document import Document
from Products.ParsedXML.ParsedXML import ParsedXML
from test_SilvaObject import hack_create_user

# awful HACK
def _getCopy(self, container):
    """A hack to make copy & paste work (used by create_copy())
    """
    return ParsedXML(self.id, self.index_html())

def _verifyObjectPaste(self, ob):
    return

class VersionedContentTestCase(unittest.TestCase):
    def setUp(self):
        
        # awful HACK to support manage_clone
        ParsedXML._getCopy = _getCopy
        Document._verifyObjectPaste = _verifyObjectPaste
        
        get_transaction().begin()
        self.connection = Zope.DB.open()
        try:
            self.root = makerequest.makerequest(self.connection.root()
                                                ['Application'])
            # awful hack: add a user who may own the 'index'
            # of the test containers
            hack_create_user(self.root)
            self.root.manage_addProduct['Silva'].manage_addRoot(
                'root', 'Root')
            self.sroot = self.root.root
            add = self.sroot.manage_addProduct['Silva']
            add.manage_addDocument('document', 'Document')
            self.document = self.sroot.document
        except:
            self.tearDown()
            raise
        
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()
    
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
        # fake present of REQUEST
        document.REQUEST = None
        document.create_copy()
        self.assertEquals(document.get_editable().id, '1')
        self.assertEquals(document.get_previewable().id, '1')
        self.assertEquals(document.get_viewable().id, '0')

    def test_workflow2(self):
        document = self.document
        self.assertEquals(document.get_editable().id, '0')
        self.assertEquals(document.get_previewable().id, '0')
        self.assertEquals(document.get_viewable(), None)
        # set publication datetime in the paste to ensure instant publication
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
        # fake present of REQUEST
        document.REQUEST = None
        document.create_copy()
        self.assertEquals(document.get_editable().id, '1')
        self.assertEquals(document.get_previewable().id, '1')
        self.assertEquals(document.get_viewable(), None)

    def test_workflow3(self):
        document = self.document
        self.assertEquals(document.get_editable().id, '0')
        self.assertEquals(document.get_previewable().id, '0')
        self.assertEquals(document.get_viewable(), None)
        # set publication datetime in the paste to ensure instant publication
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
        # fake present of REQUEST
        document.REQUEST = None
        document.create_copy()
        self.assertEquals(document.get_editable().id, '1')
        self.assertEquals(document.get_previewable().id, '1')
        self.assertEquals(document.get_viewable(), None)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersionedContentTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
