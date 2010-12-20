# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $
import SilvaTestCase


"""1 add service group aftersetup
   2 check what is on the service group method
   try manage_addGroup to the service_group
"""

class GroupTestCase(SilvaTestCase.SilvaTestCase):


    def afterSetUp(self):
        factory = self.silva.manage_addProduct['Groups']
        factory.manage_addGroupsService('service_groups', 'Groups Service')

    def group_test(self, factory_name, groupname='test_group1'):
        self.failUnless(hasattr(self.silva, 'service_groups'))
        service_groups = self.silva.service_groups

        # make a group
        factory = service_groups.manage_addProduct['Silva']
        getattr(factory, factory_name)(groupname, groupname, groupname)

        # check that isGroup works, and that the group exists
        self.failUnless(hasattr(service_groups, groupname))

        self.assertEquals(service_groups.isGroup(groupname), True)
        self.failUnless(groupname in service_groups.listAllGroups())

        group = getattr(service_groups, groupname)
        self.failUnless(group.isValid())

        # add a duplicate group
        self.assertRaises(ValueError,
                          factory.manage_addProduct['Silva'].manage_addGroup,
                          groupname, groupname, groupname)

        # delete group
        service_groups.manage_delObjects([groupname])
        self.assertEquals(service_groups.isGroup(groupname), False)


    def test_group(self):
        self.group_test('manage_addGroup')


    def test_ipgroup(self):
        self.group_test('manage_addIPGroup')


    def test_virtualgroup(self):
        self.group_test('manage_addVirtualGroup')


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GroupTestCase))
    return suite
    
