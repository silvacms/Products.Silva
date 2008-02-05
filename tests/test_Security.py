# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.21 $
from Testing import ZopeTestCase
from Products.Silva.tests import SilvaTestCase

from Products.Silva import Folder
from Products.Silva import roleinfo
from Products.SilvaDocument import Document

class SecurityTestCase(SilvaTestCase.SilvaTestCase):
    """Test the Security interface.
    """

    
    def afterSetUp(self):
        self.doc1 = doc1 = self.add_document(self.root, 'doc1', 'Doc1')
        self.doc2 = doc2 = self.add_document(self.root, 'doc2', 'Doc2')
        self.doc3 = doc3 = self.add_document(self.root, 'doc3', 'Doc3')
        self.folder4 = folder4 = self.add_folder(self.root,
                         'folder4', 'Folder4')
        self.publication5 = publication5 = self.add_publication(self.root,
                         'publication5', 'Publication5')
        self.subdoc = subdoc = self.add_folder(folder4,
                         'subdoc', 'Subdoc')
        self.subfolder = subfolder = self.add_folder(folder4,
                         'subfolder', 'Subfolder')
        self.subsubdoc = subsubdoc = self.add_document(subfolder,
                         'subsubdoc', 'Subsubdoc')
        # add some users
        self.root.acl_users._doAddUser(
            'foo', 'silly', 'Anonymous', [])
        self.root.acl_users._doAddUser(
            'bar', 'sillytoo', 'Anonymous', [])
        # we are assuming 'author' and 'editor' are the only two 
        # interesting roles that will be returned by sec_get_roles()
        #self.root._addRole('Author')
        #self.root._addRole('Editor')

    def assertSameEntries(self, list1, list2, msg=''):
        # FIXME: should we check for duplicates? not necessary for
        # current case
        self.assert_(len(list1) == len(list2),
                     msg=msg+('\nlist1 %s not equal to list 2 %s' % (str(list1), str(list2)) ) )
        for entry in list1:
            self.assert_(entry in list2, msg=('entry %s in list 1 not in %s' % (entry, str(list2)) ) )

    def test_sec_do_nothing(self):
        # foo and bar don't have any relevant roles anywhere
        self.assertSameEntries([],
                               self.doc1.sec_get_roles_for_userid('foo'))
        self.assertSameEntries([],
                               self.doc1.sec_get_roles_for_userid('foo'))
        self.assertSameEntries([],
                               self.doc1.sec_get_roles_for_userid('bar'))

        self.assertSameEntries([], self.root.sec_get_userids())
        
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

    def test_clean_stale_mappings(self):
        # test the cleanup of locally assigned roles
        self.folder4.sec_assign('foo', 'Author')
        self.folder4.sec_assign('foo', 'Editor')
        self.folder4.sec_assign('bar', 'Editor')
        self.assertSameEntries(['foo','bar'],
                               self.folder4.sec_get_userids())

        self.root.acl_users.userFolderDelUsers(['foo'])
        # XXX it would not be critical if this assertion would fail
        self.assertSameEntries(['foo','bar'],
                               self.folder4.sec_get_userids())
        self.folder4.sec_clean_roles()
        self.assertSameEntries(['bar'],
                               self.folder4.sec_get_userids())


    def test_sec_get_roles(self):
        self.assertSameEntries(
            roleinfo.ASSIGNABLE_ROLES,
            self.root.sec_get_roles())
        
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SecurityTestCase))
    return suite

