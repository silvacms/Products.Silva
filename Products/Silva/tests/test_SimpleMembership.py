# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import urllib

from zope.interface.verify import verifyObject
from zope.component import queryUtility
from silva.core.services.interfaces import IMemberService
from Products.Silva.testing import FunctionalLayer, TestCase


class SimpleMembershipTestCase(TestCase):
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
        self.assertEqual(service.get_member('manager').userid(), 'manager')
        self.assertEqual(service.get_member('viewer').userid(), 'viewer')
        self.assertEqual(service.get_member('delta'), None)

    def test_find_members(self):
        service = queryUtility(IMemberService)
        members = service.find_members('manager')
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].userid(), 'manager')

        members = service.find_members('ed')
        self.assertEqual(len(members), 2)
        userids = sorted(map(lambda m: m.userid(), members))
        self.assertEqual(userids, ['chiefeditor', 'editor'])

    def test_avatar(self):
        # XXX Data code should not generate HTML.
        #service = queryUtility(IMemberService)
        service = self.root.service_members

        user = service.get_member('manager')
        self.assertEqual(None, user.avatar())

        self.assertXMLEqual(
            user.avatar_tag(),
            '<img src="' + self.root.get_root_url() + '/globals/avatar.png" alt="manager\'s avatar" title="manager\'s avatar" style="height: 32px; width: 32px" />')
        user.set_email('user@example.com')
        self.assertEqual('user@example.com', user.avatar())
        self.assertXMLEqual(
            user.avatar_tag(),
            '<img src="https://secure.gravatar.com/avatar.php?default=' + urllib.quote(self.root.get_root_url(),'') + '%2Fglobals%2Favatar.png&size=32&gravatar_id=b58996c504c5638798eb6b511e6f49af" alt="manager\'s avatar" title="manager\'s avatar" style="height: 32px; width: 32px" />')

        self.assertXMLEqual(
            user.extra('avatar_tag:16'),
            '<img src="https://secure.gravatar.com/avatar.php?default=' + urllib.quote(self.root.get_root_url(),'') + '%2Fglobals%2Favatar.png&size=16&gravatar_id=b58996c504c5638798eb6b511e6f49af" alt="manager\'s avatar" title="manager\'s avatar" style="height: 16px; width: 16px" />')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SimpleMembershipTestCase))
    return suite
