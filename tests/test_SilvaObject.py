# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.12 $
import unittest
import Zope
#import ZODB
#import OFS.Application
from Testing import makerequest
# access "internal" class to fake request authentification
from AccessControl.User import SimpleUser
#from Products.Silva import Document, Folder, Root #, Ghost, Publication

# Awful hack: add an authenticated user into the request.
def hack_add_user(REQUEST):
    # maybe add some testing roles here ?
    REQUEST.AUTHENTICATED_USER=SimpleUser(name='TestUser',password='TestUserPasswd', roles =(), domains=())

class SilvaObjectTestCase(unittest.TestCase):
    """Test the SilvaObject interface.
    """
    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = makerequest.makerequest(self.connection.root()['Application'])
        # awful hack: add a user who may own the 'index' of the test containers
        hack_add_user(self.root.REQUEST)        
        self.root.manage_addProduct['Silva'].manage_addRoot('root', 'Root')
        self.sroot = self.root.root
        add = self.sroot.manage_addProduct['Silva']
        
        add.manage_addDocument('document',
                               'Document')
        add.manage_addFolder('folder',
                             'Folder')
        add.manage_addPublication('publication',
                                  'Publication')
        self.document = self.sroot.document
        self.folder = self.sroot.folder
        self.publication = self.sroot.publication
        # add some stuff to test breadcrumbs
        self.folder.manage_addProduct['Silva'].manage_addFolder('subfolder', 'Subfolder')
        self.subfolder = self.folder.subfolder
        self.subfolder.manage_addProduct['Silva'].manage_addDocument('subsubdoc', 'Subsubdoc')
        self.subsubdoc = self.subfolder.subsubdoc
        
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

    def test_set_title(self):
        self.document.set_title('Document2')
        self.assertEquals(self.document.get_title(), 'Document2')
        self.folder.set_title('Folder2')
        self.assertEquals(self.folder.get_title(), 'Folder2')
        self.assertEquals(self.folder.index.get_title(), 'Folder2')
        self.sroot.set_title('Root2')
        self.assertEquals(self.sroot.get_title(), 'Root2')
        self.publication.set_title('Publication2')
        self.assertEquals(self.publication.get_title(), 'Publication2')

        self.folder.index.set_title('Set by default')
        self.assertEquals(self.folder.index.get_title(),
                          'Set by default')
        self.assertEquals(self.folder.get_title(),
                          'Set by default')
        
    def test_title(self):
        self.assertEquals(self.document.get_title(), 'Document')
        self.assertEquals(self.folder.get_title(), 'Folder')
        self.assertEquals(self.sroot.get_title(), 'Root')
        self.assertEquals(self.publication.get_title(), 'Publication')
        self.assertEquals(self.folder.index.get_title(), 'Folder')

    def test_title2(self):
        # set title through document metadata, perhaps this should
        # move to a different test suite
        self.assertEquals(self.document.get_metadata('document_title'), 'Document')
        self.document.set_metadata('document_title', 'Foo')
        self.assertEquals('Foo', self.document.get_metadata('document_title'))
        self.assertEquals('Foo', self.document.get_title())
        
    #def test_get_creation_datetime(self):
    #    pass

    #def test_get_modification_datetime(self):
    #    pass

    def test_get_breadcrumbs(self):
        self.assertEquals([self.sroot],
                          self.sroot.get_breadcrumbs())
        self.assertEquals([self.sroot, self.document],
                          self.document.get_breadcrumbs())
        self.assertEquals([self.sroot, self.publication],
                          self.publication.get_breadcrumbs())
        self.assertEquals([self.sroot, self.folder],
                          self.folder.get_breadcrumbs())
        self.assertEquals([self.sroot, self.folder, self.subfolder],
                          self.subfolder.get_breadcrumbs())
        self.assertEquals([self.sroot, self.folder,
                           self.subfolder, self.subsubdoc],
                          self.subsubdoc.get_breadcrumbs())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaObjectTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
