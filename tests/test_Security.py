import unittest
import Zope
from DateTime import DateTime
from Products.Silva import Interfaces, Document, Folder

def add_helper(object, typename, id, title):
    getattr(object.manage_addProduct['Silva'], 'manage_add%s' % typename)(
        id, title)
    return getattr(object, id)
       
class SecurityTestCase(unittest.TestCase):
    """Test the Security interface.
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
        # add a user folder
        self.sroot.manage_addUserFolder()
        # add some users
        self.sroot.acl_users.userFolderAddUser('foo', 'silly', 'Anonymous', [])
        self.sroot.acl_users.userFolderAddUser('bar', 'sillytoo', 'Anonymous', [])
        # we are assuming 'author' and 'editor' are the only two interesting roles
        # that will be returned by sec_get_roles()
        self.sroot._addRole('Author')
        self.sroot._addRole('Editor')
        
    def tearDown(self):
        get_transaction().abort()
        self.connection.close()

    def assertSameEntries(self, list1, list2):
        # FIXME: should we check for duplicates? not necessary for
        # current case
        self.assert_(len(list1) == len(list2))
        for entry in list1:
            self.assert_(entry in list2)

    def test_sec_do_nothing(self):
        # foo and bar don't have any relevant roles anywhere
        self.assertSameEntries([],
                               self.doc1.sec_get_roles_for_userid('foo'))
        self.assertSameEntries([],
                               self.doc1.sec_get_roles_for_userid('foo'))
        self.assertSameEntries([],
                               self.doc1.sec_get_roles_for_userid('bar'))

        self.assertSameEntries([], self.sroot.sec_get_userids())
        
    def test_sec_assign(self):
        self.doc1.sec_assign('foo', 'Author')
        self.doc1.sec_assign('foo', 'Editor')

        self.assertSameEntries(['foo'],
                               self.doc1.sec_get_userids())
        self.assertSameEntries(['Author', 'Editor'],
                               self.doc1.sec_get_roles_for_userid('foo'))
          
    def test_sec_revoke(self):
        self.doc1.sec_assign('foo', 'Author')
        self.doc1.sec_assign('foo', 'Editor')

        self.doc1.sec_revoke('foo', ['Editor'])
        self.assertSameEntries(['Author'],
                               self.doc1.sec_get_roles_for_userid('foo'))
        self.assertSameEntries(['foo'],
                               self.doc1.sec_get_userids())
        self.doc1.sec_revoke('foo', ['Author'])
        self.assertSameEntries([],
                               self.doc1.sec_get_roles_for_userid('foo'))
        self.assertSameEntries([],
                               self.doc1.sec_get_userids())

    def test_sec_remove(self):
        self.doc1.sec_assign('foo', 'Author')
        self.doc1.sec_assign('foo', 'Editor')
        self.doc1.sec_remove('foo')
        
        self.assertSameEntries([],
                               self.doc1.sec_get_userids())

    def test_sec_get_roles(self):
        self.assertSameEntries(['Author', 'Editor', 'ChiefEditor', 'Manager'],
                               self.sroot.sec_get_roles())
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SecurityTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
