# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
import unittest
import Zope
#import ZODB
#import OFS.Application
from Testing import makerequest
# access "internal" class to fake request authentification
from AccessControl.User import SimpleUser
#from Products.Silva import Document, Folder, Root #, Ghost, Publication

class SimpleMembershipTestCase(unittest.TestCase):
    """Test simple membership.
    """

    def setUp(self):
        get_transaction().begin()
        self.connection = Zope.DB.open()
        self.root = makerequest.makerequest(
            self.connection.root()['Application'])
        self.root.manage_addProduct['Silva'].manage_addRoot('root', 'Root')
        self.sroot = self.root.root
        self.sroot.manage_addFolder('Members')
        self.sroot.manage_addProduct['Silva'].manage_addSimpleMemberService(
            'service_members')
        self.members = self.sroot.Members
        # add user folder and some test users
        self.sroot.manage_addUserFolder()
        acl_users = self.sroot.acl_users
        acl_users._addUser('alpha', 'alpha', 'alpha', [], [])
        acl_users._addUser('beta', 'beta', 'beta', [], [])
        acl_users._addUser('gamma', 'gamma', 'gamma', [], [])
        acl_users._addUser('alpha2', 'alpha2', 'alpha2', [], [])

    def tearDown(self):
        get_transaction().abort()
        self.connection.close()
    
    def test_is_user(self):
        service_members = self.sroot.service_members
        self.assert_(service_members.is_user('alpha'))
        self.assert_(service_members.is_user('beta'))
        self.assert_(service_members.is_user('gamma'))
        self.assert_(service_members.is_user('alpha2'))
        self.assert_(not service_members.is_user('delta'))
        
    def test_get_member(self):
        service_members = self.sroot.service_members
        self.assertEquals(service_members.get_member('alpha').userid(), 'alpha')
        self.assertEquals(service_members.get_member('beta').userid(), 'beta')
        self.assertEquals(service_members.get_member('delta'), None)

    def test_find_members(self):
        service_members = self.sroot.service_members
        members = service_members.find_members('beta')
        self.assertEquals(len(members), 1)
        self.assertEquals(members[0].userid(), 'beta')

        members = service_members.find_members('alpha')
        self.assertEquals(len(members), 2)
        self.assert_((members[0].userid() == 'alpha' and
                      members[1].userid() == 'alpha2') or
                     (members[0].userid() == 'alpha2' and
                      members[1].userid() == 'alpha'))
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SimpleMembershipTestCase, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
