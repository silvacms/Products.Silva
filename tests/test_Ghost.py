import unittest
import Zope
from Products.Silva import Interfaces
from DateTime import DateTime

def add_helper(object, typename, id, title):
    getattr(object.manage_addProduct['Silva'], 'manage_add%s' % typename)(id, title)
    return getattr(object, id)

def preview(self):
    pass

def view(self):
    pass

class GhostTestCase(unittest.TestCase):
    """Test the Ghost object.
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

    def test_ghost(self):
        ghost = self.sroot.manage_addProduct['Silva'].manage_addGhost('ghost1',
                                                                      '/root/doc1')
        self.assertEquals('', ghost.preview())
        self.assertEquals(None, ghost.view())

        self.assertEquals('/root/doc1', ghost.get_editable())
        self.assert_(not ghost.get_previewable())
        self.assert_(not ghost.get_viewable())
        self.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc1.approve_version()
        self.assertEquals('0', ghost.get_previewable().id)
        ghost.set_unapproved_version_publication_datetime(DateTime() - 1)
        ghost.approve_version()
        self.assert_(not ghost.get_editable())
        self.assertEquals('0', ghost.get_previewable().id)
        self.assertEquals('0', ghost.get_viewable().id)
        self.doc1.create_copy()
        # nothing should've changed for ghost
        self.assert_(not ghost.get_editable())
        self.assertEquals('Doc1', ghost.get_previewable().title())
        self.assertEquals('Doc1', ghost.get_viewable().title())
        # we're breaking into the implementation by looking at the version
        # id here..
        self.doc1.set_unapproved_version_publication_datetime(DateTime() - 1)
        self.doc1.approve_version()
        self.as
        
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GhostTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
