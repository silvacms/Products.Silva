# Copyright (c) 2003-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $

import SilvaTestCase


"""1 add service group aftersetup
   2 check what is on the service group method
   try manage_addGroup to the service_group
"""

class BaseGroupTestCase(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.silva.manage_addProduct['Groups'].manage_addGroupsService('service_groups', 'Groups Service')

class GroupTestCase(BaseGroupTestCase):
        
    def test_create(self):
        self.failUnless(hasattr(self.silva, 'service_groups'))
        # make a group
        self.silva.service_groups.manage_addProduct['Silva'].manage_addGroup('test_group1', 'test_group1', 'test_group1')
        # check that isGroup works, and that the group exists
        self.assertEquals(self.silva.service_groups.isGroup('test_group1'), True)
        # add a duplicate group
        self.assertRaises(ValueError,
                         self.silva.service_groups.manage_addProduct['Silva'].manage_addGroup,
                         'test_group1', 'test_group1', 'test_group1')
        self.silva.service_groups.manage_delObjects(['test_group1'])
        self.assertEquals(self.silva.service_groups.isGroup('test_group1'), False)

class IPGroupTestCase(BaseGroupTestCase):

    def test_create(self):
        self.failUnless(hasattr(self.silva, 'service_groups'))
        # make a group
        self.silva.service_groups.manage_addProduct['Silva'].manage_addIPGroup('test_group1', 'test_group1', 'test_group1')
        # check that isGroup works, and that the group exists
        self.assertEquals(self.silva.service_groups.isGroup('test_group1'), True)
        # add a duplicate group
        self.assertRaises(ValueError,
                         self.silva.service_groups.manage_addProduct['Silva'].manage_addGroup,
                         'test_group1', 'test_group1', 'test_group1')
        self.silva.service_groups.manage_delObjects(['test_group1'])
        self.assertEquals(self.silva.service_groups.isGroup('test_group1'), False)

class VirtualGroupTestCase(BaseGroupTestCase):

    def test_create(self):
        self.failUnless(hasattr(self.silva, 'service_groups'))
        # make a group
        self.silva.service_groups.manage_addProduct['Silva'].manage_addVirtualGroup('test_group1', 'test_group1', 'test_group1')
        # check that isGroup works, and that the group exists
        self.assertEquals(self.silva.service_groups.isGroup('test_group1'), True)
        # add a duplicate group
        self.assertRaises(ValueError,
                         self.silva.service_groups.manage_addProduct['Silva'].manage_addGroup,
                         'test_group1', 'test_group1', 'test_group1')
        self.silva.service_groups.manage_delObjects(['test_group1'])
        self.assertEquals(self.silva.service_groups.isGroup('test_group1'), False)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GroupTestCase))
    suite.addTest(unittest.makeSuite(IPGroupTestCase))
    suite.addTest(unittest.makeSuite(VirtualGroupTestCase))
    return suite
    
