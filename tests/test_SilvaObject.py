import unittest
import Zope
#import ZODB
#import OFS.Application
from Products.Silva import Document, Folder, Root #, Ghost, Publication

class SilvaObjectTestCase(unittest.TestCase):
    """Test the SilvaObject interface.
    """
    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = self.connection.root()['Application']
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
        
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

    def test_set_title(self):
        self.document.set_title('Document2')
        self.assertEquals(self.document.title(), 'Document2')
        self.folder.set_title('Folder2')
        self.assertEquals(self.folder.title(), 'Folder2')
        self.assertEquals(self.folder.default.title(), 'Folder2')
        self.sroot.set_title('Root2')
        self.assertEquals(self.sroot.title(), 'Root2')
        self.publication.set_title('Publication2')
        self.assertEquals(self.publication.title(), 'Publication2')

        self.folder.default.set_title('Set by default')
        self.assertEquals(self.folder.default.title(),
                          'Set by default')
        self.assertEquals(self.folder.title(),
                          'Set by default')
        
    def test_title(self):
        self.assertEquals(self.document.title(), 'Document')
        self.assertEquals(self.folder.title(), 'Folder')
        self.assertEquals(self.sroot.title(), 'Root')
        self.assertEquals(self.publication.title(), 'Publication')
        self.assertEquals(self.folder.default.title(), 'Folder')
        
    def test_get_creation_datetime(self):
        pass

    def test_get_modification_datetime(self):
        pass

    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaObjectTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
