# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.20 $
import unittest
from DateTime import DateTime
import Zope
Zope.startup()

#import ZODB
#import OFS.Application
from Testing import makerequest
# access "internal" class to fake request authentification
from AccessControl.User import SimpleUser
from Products.Silva.Document import Document, DocumentVersion

# awful HACK
def _getCopy(self, container):
    """A hack to make copy & paste work (used by create_copy())
    """
    return DocumentVersion(self.id, self.get_title())
    
def _verifyObjectPaste(self, ob):
    return

# Awful hack: add an authenticated user into the request.
def hack_create_user(root):
    from AccessControl import User
    from AccessControl.SecurityManagement import newSecurityManager
    
    # we can restore the existing user latter if need be, we don't for now.

    if not hasattr(root, 'acl_users'):
        root.manage_addUserFolder()
    root.acl_users.userFolderAddUser(name='TestUser', password='TestUserPasswd', roles=(), domains=())
    
    # get the new user
    user = root.acl_users.getUser('TestUser').__of__(root.acl_users)

    # sign on the new user
    try: req = self.REQUEST
    except: req = None
    newSecurityManager(req, user)

    # maybe add some testing roles here ?
    
    REQUEST = root.REQUEST
    REQUEST.AUTHENTICATED_USER=root.acl_users.getUser('TestUser')

class SilvaObjectTestCase(unittest.TestCase):
    """Test the SilvaObject interface.
    """
    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()

        # awful HACK to support manage_clone
        DocumentVersion._getCopy = _getCopy
        Document._verifyObjectPaste = _verifyObjectPaste
        
        try:
            self.root = makerequest.makerequest(
                self.connection.root()['Application'])
            self.root.REQUEST['URL1'] = ''
            self.REQUEST = self.root.REQUEST
            # awful hack: add a user who may own the 'index'
            # of the test containers
            hack_create_user(self.root)
            self.root.manage_addProduct['Silva'].manage_addRoot(
                'root', 'Root')
            self.sroot = self.root.root            
            add = self.sroot.manage_addProduct['Silva']
            add.manage_addDocument('document',
                                   'Document')
            add.manage_addFolder('folder',
                                 'Folder')
            add.manage_addPublication('publication',
                                      'Publication')
            add.manage_addDocument('document2',
                                   '')
            self.document = self.sroot.document
            self.document2 = self.sroot.document2
            self.folder = self.sroot.folder
            self.publication = self.sroot.publication
            # add some stuff to test breadcrumbs
            self.folder.manage_addProduct['Silva'].manage_addFolder(
                'subfolder', 'Subfolder')
            self.subfolder = self.folder.subfolder
            self.subfolder.manage_addProduct['Silva'].manage_addDocument(
                'subsubdoc', 'Subsubdoc')
            self.subsubdoc = self.subfolder.subsubdoc
        except:
            self.tearDown()
            raise

    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

##     def test_set_title(self):
##         self.document.set_title('Document2')
##         self.assertEquals(self.document.get_title_editable(), 'Document2')
##         self.folder.set_title('Folder2')
##         self.assertEquals(self.folder.get_title_editable(), 'Folder2')
##         self.assertEquals(self.folder.index.get_title_editable(), 'Folder2')
##         self.sroot.set_title('Root2')
##         self.assertEquals(self.sroot.get_title_editable(), 'Root2')
##         self.publication.set_title('Publication2')
##         self.assertEquals(self.publication.get_title_editable(), 'Publication2')

##         self.folder.index.set_title('Set by default')
##         self.assertEquals(self.folder.index.get_title(),
##                           'Set by default')
##         self.assertEquals(self.folder.get_title(),
##                           'Set by default')
        
##     def test_title(self):
##         self.assertEquals(self.document.get_title_editable(), 'Document')
##         self.assertEquals(self.folder.get_title_editable(), 'Folder')
##         self.assertEquals(self.sroot.get_title_editable(), 'Root')
##         self.assertEquals(self.publication.get_title_editable(), 'Publication')
##         self.assertEquals(self.folder.index.get_title_editable(), 'Folder')
        
##     def test_title3(self):
##         # Test get_title_or_id
##         self.assertEquals(self.document.get_title_or_id_editable(), 'Document')
##         self.assertEquals(self.document2.get_title_or_id_editable(), 'document2')

    def test_title4(self):
        self.folder.index.set_unapproved_version_publication_datetime(
            DateTime() - 1)
        self.folder.index.approve_version()
        self.folder.index.create_copy()
        self.folder.index.set_title('folder 2')
        self.assertEquals(self.folder.get_title_editable(), 'folder 2')
        self.assertEquals(self.folder.index.get_title_editable(), 'folder 2')
        self.assertEquals(self.folder.get_title(), 'Folder')
        self.assertEquals(self.folder.index.get_title(), 'Folder')
        
    def test_title5(self):
        self.folder.index.set_unapproved_version_publication_datetime(
            DateTime() - 1)
        self.folder.index.approve_version()
        self.folder.index.create_copy()
        self.folder.set_title('folder 2')
        self.assertEquals(self.folder.get_title_editable(), 'folder 2')
        self.assertEquals(self.folder.index.get_title_editable(), 'folder 2')
        self.assertEquals(self.folder.get_title(), 'Folder')
        self.assertEquals(self.folder.get_title(), 'Folder')

    def test_title6(self):
        self.folder.set_title('folder 2')
        self.assertEquals(self.folder.get_title_editable(), 'folder 2')
           
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
