import unittest
import Zope
#import ZODB
#import OFS.Application
from Products.Silva import Document, Folder, Root #, Ghost, Publication
from Products.Silva import Interfaces

def add_helper(object, typename, id, title):
    getattr(object.manage_addProduct['Silva'], 'manage_add%s' % typename)(id, title)
    return getattr(object, id)

class ContainerTestCase(unittest.TestCase):
    """Test the Container interface.
    """
    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = self.connection.root()['Application']
        self.sroot = sroot = add_helper(self.root, 'Root', 'root', 'Root')
        self.doc1 = doc1 = add_helper(sroot, 'Document', 'doc1', 'Doc1')
        self.doc2 = doc2 = add_helper(sroot, 'Document', 'doc2', 'Doc2')
        self.doc3 = doc3 = add_helper(sroot, 'Document', 'doc3', 'Doc3')
        self.folder4 = folder4 = add_helper(sroot, 'Folder', 'folder4', 'Folder4')
        self.publication5 = publication5 = add_helper(sroot, 'Publication',
                                                      'publication5', 'Publication5')
        self.subdoc = subdoc = add_helper(folder4, 'Document', 'subdoc', 'Subdoc')
        self.subfolder = subfolder = add_helper(folder4, 'Folder', 'subfolder', 'Subfolder')
        self.subsubdoc = subsubdoc = add_helper(subfolder, 'Document', 'subsubdoc', 'Subsubdoc')
        self.subdoc2 = subdoc2 = add_helper(publication5, 'Document', 'subdoc2', 'Subdoc2')
        
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

    def test_get_default(self):
        doc = self.folder4.get_default()
        self.assertEquals(doc.title(), 'Folder4')
        self.assert_(Interfaces.Content.isImplementedBy(doc),
                     'doc is not a Content object')
        self.assert_(doc.is_default(),
                     'Default document is_default gives false')

    def test_get_ordered_publishables(self):
        l = [self.doc1, self.doc2, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        l = [self.subdoc, self.subfolder]
        self.assertEquals(self.folder4.get_ordered_publishables(),
                          l)

    def test_get_nonactive_publishables(self):
        self.doc2.deactivate()
        ordered = [self.doc1, self.doc3, self.folder4, self.publication5]
        nonactive = [self.doc2]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          ordered)
        self.assertEquals(self.sroot.get_nonactive_publishables(),
                          nonactive)
        # deactivating something inactive shouldn't do anything
        self.doc2.deactivate()
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          ordered)
        self.assertEquals(self.sroot.get_nonactive_publishables(),
                          nonactive)
        self.doc2.activate()
        ordered = [self.doc1, self.doc3, self.folder4, self.publication5,
                   self.doc2]
        nonactive = []
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          ordered)
        self.assertEquals(self.sroot.get_nonactive_publishables(),
                          nonactive)
        # activating something active shouldn't do anything
        self.doc2.activate()
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          ordered)
        self.assertEquals(self.sroot.get_nonactive_publishables(),
                          nonactive)
        
    def test_get_assets(self):
        pass # FIXME: make asset object

    def test_get_tree(self):
        l = [(0, self.doc1), (0, self.doc2), (0, self.doc3),
             (0, self.folder4), (1, self.subdoc), (1, self.subfolder),
             (2, self.subfolder.subsubdoc), (0, self.publication5)]
        self.assertEquals(self.sroot.get_tree(),
                          l)
        l = [(0, self.folder4), (1, self.subfolder),
             (0, self.publication5)]
        self.assertEquals(self.sroot.get_container_tree(),
                          l)

    def test_move_object_up(self):
        r = self.sroot.move_object_up('doc2')
        l = [self.doc2, self.doc1, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(r)
        r = self.sroot.move_object_up('doc2')
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(not r)

        r = self.sroot.move_object_up('folder4')
        l = [self.doc2, self.doc1, self.folder4, self.doc3, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(r)
        self.doc1.deactivate()
        self.assert_(not self.sroot.move_object_up('doc1'))

    def test_move_object_down(self):
        r = self.sroot.move_object_down('doc2')
        l = [self.doc1, self.doc3, self.doc2, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(r)
        r = self.sroot.move_object_down('publication5')
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(not r)

        r = self.sroot.move_object_down('folder4')
        l = [self.doc1, self.doc3, self.doc2, self.publication5, self.folder4]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        self.assert_(r)
        self.doc1.deactivate()
        self.assert_(not self.sroot.move_object_down('doc1'))

    def test_move_to_single_item_down(self):
        # move of a single item down
        r = self.sroot.move_to(['doc2'], 4)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.folder4, self.doc2, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
    def test_move_to_single_item_up(self):
        # move of a single item up
        r = self.sroot.move_to(['doc3'], 1)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.doc2, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)

    def test_move_to_multiple_consecutive(self):
        # move of multiple consecutive items
        r = self.sroot.move_to(['doc3', 'folder4'], 0)
        self.assert_(r)
        l = [self.doc3, self.folder4, self.doc1, self.doc2, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)

    def test_move_to_multiple_consecutive_wrong_order(self):
        r = self.sroot.move_to(['folder4', 'doc3'], 0)
        self.assert_(r)
        l = [self.doc3, self.folder4, self.doc1, self.doc2, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)

    def test_move_to_multiple_nonconsecutive(self):
        r = self.sroot.move_to(['doc1', 'publication5', 'doc3'], 4)
        self.assert_(r)
        l = [self.doc2, self.folder4, self.doc1, self.doc3, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
    
    def test_move_to_all(self):
        r = self.sroot.move_to(['doc1', 'doc2', 'doc3', 'folder4', 'publication5'], 1)
        self.assert_(r)
        l = [self.doc1, self.doc2, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        
    def test_move_to_end(self):
        r = self.sroot.move_to(['doc2'], 5)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.folder4, self.publication5, self.doc2]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        
    def test_move_to_wrong_indexes(self):
        r = self.sroot.move_to(['doc2'], 100)
        self.assert_(r)
        l = [self.doc1, self.doc3, self.folder4, self.publication5, self.doc2]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        
    def test_move_wrong_ids(self):
        r = self.sroot.move_to(['foo'], 1)
        self.assert_(not r)
        r = self.sroot.move_to(['doc2', 'foo'], 1)
        self.assert_(not r)
        l = [self.doc1, self.doc2, self.doc3, self.folder4, self.publication5]
        self.assertEquals(self.sroot.get_ordered_publishables(),
                          l)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContainerTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
