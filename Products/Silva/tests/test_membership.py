# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.interface.verify import verifyObject
from zope.component import queryUtility
from silva.core.interfaces import IEditableMember, IMember
from silva.core.services.interfaces import IMemberService

from Products.Silva.testing import FunctionalLayer


class SimpleMembershipTestCase(unittest.TestCase):
    """Test simple membership.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_service(self):
        service = queryUtility(IMemberService)
        self.assertTrue(verifyObject(IMemberService, service))
        self.assertEqual(self.root.service_members, service)

    def test_is_user(self):
        service = queryUtility(IMemberService)
        self.assertTrue(service.is_user('manager'))
        self.assertTrue(service.is_user('viewer'))
        self.assertTrue(service.is_user('reader'))
        self.assertTrue(service.is_user('editor'))
        self.assertFalse(service.is_user('delta_forces'))

    def test_get_member(self):
        service = queryUtility(IMemberService)
        members = self.root.Members
        self.assertEqual(members._getOb('viewer', None), None)
        member = service.get_member('viewer')
        self.assertTrue(verifyObject(IMember, member))
        self.assertTrue(verifyObject(IEditableMember, member))
        self.assertEqual(member.userid(), 'viewer')
        self.assertEqual(member.fullname(), 'viewer')
        self.assertEqual(member.email(), None)
        self.assertEqual(members._getOb('viewer'), member)
        member.set_fullname('Arthur de Pandragor')
        self.assertEqual(member.fullname(), 'Arthur de Pandragor')

    def test_get_member_unexisting(self):
        service = queryUtility(IMemberService)
        members = self.root.Members
        self.assertEqual(members._getOb('delta', None), None)
        self.assertEqual(service.get_member('delta'), None)
        self.assertEqual(members._getOb('delta', None), None)

    def get_cached_member(self):
        service = queryUtility(IMemberService)
        members = self.root.Members
        self.assertEqual(members._getOb('editor', None), None)
        member = service.get_cached_member('editor')
        self.assertTrue(verifyObject(IMember, member))
        self.assertFalse(IEditableMember.providedBy(member))
        self.assertEqual(member.userid(), 'editor')
        self.assertEqual(member.fullname(), 'editor')
        self.assertEqual(member.email(), None)

        # Changing the original member object doesn't affect the
        # cached one.
        original = members._getOb('editor')
        self.assertTrue(verifyObject(IMember, original))
        self.assertTrue(verifyObject(IEditableMember, original))
        self.assertNotEqual(original, member)
        original.set_fullname('Arthur de Pandragor')
        self.assertEqual(member.fullname(), None)

    def get_cached_member_unexisting(self):
        service = queryUtility(IMemberService)
        member = service.get_cached_member('delta')
        members = self.root.Members
        self.assertTrue(verifyObject(IMember, member))
        self.assertFalse(IEditableMember.providedBy(member))
        self.assertEqual(member.userid(), 'unknown')
        self.assertEqual(member.fullname(), 'unknown')
        self.assertEqual(member.email(), None)
        self.assertEqual(members._getOb('delta', None), None)

    def test_find_members(self):
        service = queryUtility(IMemberService)
        members = service.find_members('manager')
        self.assertItemsEqual(
            map(lambda m: m.userid(), members),
            ['manager'])

        members = service.find_members('ed')
        self.assertItemsEqual(
            map(lambda m: m.userid(), members),
            ['chiefeditor', 'editor'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SimpleMembershipTestCase))
    return suite
