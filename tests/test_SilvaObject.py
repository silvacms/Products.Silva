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
        add = self.root.manage_addProduct['Silva']
        add.manage_addDocument('document', 'Document')
        add.manage_addFolder('folder', 'Folder')
        add.manage_addRoot('root', 'Root')
        add.manage_addPublication('publication', 'Publication')
        
        #self.document = Document.Document('document', 'Document')
        #self.default = Fol
        #self.folder = Folder.Folder('folder', 'Folder')
        #self.root = Root.Root('root', 'Root')
        #self.ghost = Ghost.Ghost('ghost', 'Ghost')
        #self.publication = Publication.Publication('publication', 'Publication')
        
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

    def test_set_title(self):
        self.root.document.set_title('Document2')
        self.assertEquals(self.root.document.title(), 'Document2')
        self.root.folder.set_title('Folder2')
        self.assertEquals(self.root.folder.title(), 'Folder2')
        self.assertEquals(self.root.folder.default.title(), 'Folder2')
        self.root.root.set_title('Root2')
        self.assertEquals(self.root.root.title(), 'Root2')
        self.root.publication.set_title('Publication2')
        self.assertEquals(self.root.publication.title(), 'Publication2')

        self.root.folder.default.set_title('Set by default')
        self.assertEquals(self.root.folder.default.title(),
                          'Set by default')
        self.assertEquals(self.root.folder.title(),
                          'Set by default')
        
    def test_title(self):
        self.assertEquals(self.root.document.title(), 'Document')
        self.assertEquals(self.root.folder.title(), 'Folder')
        self.assertEquals(self.root.root.title(), 'Root')
        self.assertEquals(self.root.publication.title(), 'Publication')
        self.assertEquals(self.root.folder.default.title(), 'Folder')
        
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
