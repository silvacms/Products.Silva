import unittest
import time
from DateTime import DateTime
import Zope
Zope.startup()
from Products.Silva.IVersion import IVersion
from Products.Silva.Document import Document
from Products.Silva.Folder import Folder
from Products.Silva.Image import Image

from security import OmnipotentUser
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from security import PermissiveSecurityPolicy, AnonymousUser

# this needs to be imported after startup?
from Testing.makerequest import makerequest 

class SilvaTestCase(unittest.TestCase):
    def setUp(self):
        self.silva = root.silva_test
        self.catalog = self.silva.service_catalog
        # XXX ugh would really like to avoid this..
        Document.cb_isMoveable = lambda self: 1
        Folder.cb_isMoveable = lambda self: 1
        Image.cb_isMoveable = lambda self: 1
        
    def tearDown(self):
        # delete all additional objects found later
        new_ids = []
        for id in self.silva.objectIds():
            if id not in silva_ids:
                new_ids.append(id)
        self.silva.manage_delObjects(new_ids)

        # XXX while tearDown tries to restore Silva into a
        # pristine state, in actuality there are a number
        # of things that can be done that will cause this
        # not to work properly at all. This should therefore be seen
        # as a performance hack.. It also sometimes helps with
        # debugging as it can expose bugs that otherwise would not
        # have been exposed so easily.


    def assertStatus(self, path, statuses):
        results = self.catalog.searchResults(version_status=statuses,
                                             path=path)
        # should get as many entries as statuses
        self.assertEquals(len(statuses), len(results))

        # make sure the statuses are the same
        statuses.sort()
        catalog_statuses = []
        for brain in results:
            object = brain.getObject()
            self.assert_(IVersion.isImplementedBy(object))
            catalog_statuses.append(object.version_status())
        catalog_statuses.sort()
        self.assertEquals(statuses, catalog_statuses)

    def assertPath(self, path):
        results = self.catalog.searchResults(path=path)
        for brain in results:
            if brain.getPath() == path:
                return
        self.fail()
        
    def assertNoPath(self, path):
        results = self.catalog.searchResults(path=path)
        for brain in results:
            if brain.getPath() == path:
                self.fail()
        
    def assertPristineCatalog(self):
        # the pristine catalog has a single document public
        results = self.catalog.searchResults()
        # the root itself and the index document 
        self.assertEquals(2, len(results))
        
class VersionCatalogTestCase(SilvaTestCase):
    def setUp(self):
        SilvaTestCase.setUp(self)
        self.silva.manage_addProduct['Silva'].manage_addDocument(
            'alpha', 'Alpha')
        self.alpha = self.silva.alpha
  
    def tearDown(self):
        SilvaTestCase.tearDown(self)
       
    def test_pristine(self): 
        self.silva.manage_delObjects(['alpha'])
        self.assertPristineCatalog()
        
    def test_unapproved(self):
        self.assertStatus('/silva_test/alpha', ['unapproved'])

    def test_approved(self):
        # set publication time into the future, so should be approved
        dt = DateTime() + 1
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.assertStatus('/silva_test/alpha', ['approved'])
        
    def test_public(self):
        # set publication time into the past, so should go public right away
        dt = DateTime() - 1
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.assertStatus('/silva_test/alpha', ['public'])

    def test_closed(self):
        dt = DateTime() - 1
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.alpha.close_version()
        self.assertPristineCatalog()

    def test_new(self):
        dt = DateTime() - 1
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.alpha.create_copy()
        self.assertStatus('/silva_test/alpha', ['unapproved', 'public'])
        
    def test_new_approved(self):
        dt = DateTime() - 1
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.alpha.create_copy()
        self.alpha.set_unapproved_version_publication_datetime(dt)
        self.alpha.approve_version()
        self.assertStatus('/silva_test/alpha', ['public'])

    def test_rename(self):
        self.silva.manage_renameObject('alpha', 'beta')
        self.assertStatus('/silva_test/alpha', [])
        self.assertStatus('/silva_test/beta', ['unapproved'])

    def test_copy(self):
        cb = self.silva.manage_copyObjects(['alpha'])
        self.silva.manage_pasteObjects(cb)
        self.assert_(hasattr(self.silva, 'copy_of_alpha'))
        self.assertStatus('/silva_test/alpha', ['unapproved'])
        self.assertStatus('/silva_test/copy_of_alpha', ['unapproved'])
        
    def test_cut(self):
        self.silva.manage_addProduct['Silva'].manage_addFolder('sub', 'Sub')
        cb = self.silva.manage_cutObjects(['alpha'])
        self.silva.sub.manage_pasteObjects(cb)
        self.assertStatus('/silva_test/alpha', [])
        self.assertStatus('/silva_test/sub/alpha', ['unapproved'])

class ContainerCatalogTestCase(SilvaTestCase):
    def test_folder1(self):
        self.assertNoPath('/silva_test/sub')
        self.silva.manage_addProduct['Silva'].manage_addFolder('sub', 'Sub')
        self.assertPath('/silva_test/sub')
        self.silva.manage_delObjects(['sub'])
        self.assertNoPath('/silva_test/sub')
        
    def test_folder2(self):
        self.silva.manage_addProduct['Silva'].manage_addFolder('sub', 'Sub')
        self.silva.manage_delObjects(['sub'])
        self.assertNoPath('/silva_test/sub')
        self.assertStatus('/silva_test/sub/index', [])
        
    def test_folder3(self):
        # cut & paste
        self.silva.manage_addProduct['Silva'].manage_addFolder('sub', 'Sub')
        self.silva.manage_addProduct['Silva'].manage_addFolder('sub2', 'Sub')
        cb = self.silva.manage_cutObjects(['sub'])
        self.silva.sub2.manage_pasteObjects(cb)
        self.assertStatus('/silva_test/sub2/sub/index', ['unapproved'])
        self.assertStatus('/silva_test/sub/index', [])

class AssetCatalogTestCase(SilvaTestCase):
    def test_asset1(self):
        self.silva.manage_addProduct['Silva'].manage_addImage('test', 'Test')
        self.assertPath('/silva_test/test')
        self.silva.manage_renameObject('test', 'test2')
        self.assertNoPath('/silva_test/test')
        self.assertPath('/silva_test/test2')

class MetadataCatalogTestCase(SilvaTestCase):
    def test_add(self):
        md = self.silva.service_metadata
        self.assertEquals(
            'Silva Test',
            md.getMetadataValue(
            self.silva.index.get_viewable(),
            'silva-content', 'maintitle'))
    
# XXX
# test asset cataloging
# test root cataloging

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersionCatalogTestCase, 'test'))
    suite.addTest(unittest.makeSuite(ContainerCatalogTestCase, 'test'))
    suite.addTest(unittest.makeSuite(AssetCatalogTestCase, 'test'))
    suite.addTest(unittest.makeSuite(MetadataCatalogTestCase, 'test'))
    return suite

def main():
    _policy = PermissiveSecurityPolicy()
    _oldPolicy = setSecurityPolicy(_policy)
    connection = Zope.DB.open()
    global root
    root = connection.root()['Application']
    newSecurityManager(None, AnonymousUser().__of__(root))
    root = makerequest(root)
    root.URL1 = ''
    root.REQUEST.AUTHENTICATED_USER = OmnipotentUser()
    root.manage_addProduct['Silva'].manage_addRoot(
        'silva_test', 'Silva Test')
    global silva_ids
    silva_ids = root.silva_test.objectIds()
    
    try:
        unittest.TextTestRunner().run(test_suite())        
    finally:
        get_transaction().abort()
        connection.close()
        noSecurityManager()
        setSecurityPolicy(_oldPolicy)
        
if __name__ == '__main__':
    main()
    
        
        


        
    
