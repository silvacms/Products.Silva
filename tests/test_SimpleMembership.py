# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from zope.interface.verify import verifyObject

from silva.core import interfaces
from Products.Silva.tests import  SilvaTestCase

import urllib

class SimpleMembershipTestCase(SilvaTestCase.SilvaTestCase):
    """Test simple membership.
    """

    def afterSetUp(self):
        self.members = self.root.Members
        # add user folder and some test users
        self.root.manage_addUserFolder()
        acl_users = self.root.acl_users
        acl_users._addUser('alpha', 'alpha', 'alpha', [], [])
        acl_users._addUser('beta', 'beta', 'beta', [], [])
        acl_users._addUser('gamma', 'gamma', 'gamma', [], [])
        acl_users._addUser('alpha2', 'alpha2', 'alpha2', [], [])

    def test_service(self):
        self.failUnless(verifyObject(interfaces.IMemberService,
                                     self.root.service_members))

    def test_is_user(self):
        service_members = self.root.service_members
        self.assert_(service_members.is_user('alpha'))
        self.assert_(service_members.is_user('beta'))
        self.assert_(service_members.is_user('gamma'))
        self.assert_(service_members.is_user('alpha2'))
        self.assert_(not service_members.is_user('delta'))

    def test_get_member(self):
        service_members = self.root.service_members
        self.assertEquals(service_members.get_member('alpha').userid(), 'alpha')
        self.assertEquals(service_members.get_member('beta').userid(), 'beta')
        self.assertEquals(service_members.get_member('delta'), None)

    def test_find_members(self):
        service_members = self.root.service_members
        members = service_members.find_members('beta')
        self.assertEquals(len(members), 1)
        self.assertEquals(members[0].userid(), 'beta')

        members = service_members.find_members('alpha')
        self.assertEquals(len(members), 2)
        self.assert_((members[0].userid() == 'alpha' and
                      members[1].userid() == 'alpha2') or
                     (members[0].userid() == 'alpha2' and
                      members[1].userid() == 'alpha'))

    def test_avatar(self):
        service_members = self.root.service_members
        alpha = service_members.get_member('alpha')
        self.assertEquals('', alpha.avatar())
        string = '<img src="' + self.root.get_root_url() + '/globals/avatar.png" alt="alpha\'s avatar" title="alpha\'s avatar" style="height: 32px; width: 32px" />'
        self.assertEquals(string, alpha.avatar_tag())
        alpha.set_avatar('user@example.com')
        self.assertEquals('user@example.com', alpha.avatar())
        string = '<img src="https://secure.gravatar.com/avatar.php?default=' + urllib.quote(self.root.get_root_url(),'') + '%2Fglobals%2Favatar.png&size=32&gravatar_id=b58996c504c5638798eb6b511e6f49af" alt="alpha\'s avatar" title="alpha\'s avatar" style="height: 32px; width: 32px" />'
        self.assertEquals(string, alpha.avatar_tag())
        string = '<img src="https://secure.gravatar.com/avatar.php?default=' + urllib.quote(self.root.get_root_url(),'') + '%2Fglobals%2Favatar.png&size=16&gravatar_id=b58996c504c5638798eb6b511e6f49af" alt="alpha\'s avatar" title="alpha\'s avatar" style="height: 16px; width: 16px" />'
        self.assertEquals(string, alpha.extra('avatar_tag:16'))
        

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SimpleMembershipTestCase))
    return suite

