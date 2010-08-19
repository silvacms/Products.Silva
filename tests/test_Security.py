# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core.interfaces import IAccessSecurity
from zope import component
from zope.interface.verify import verifyObject

from AccessControl import getSecurityManager
from Products.Silva.testing import FunctionalLayer


class AccessSecurityTestCase(unittest.TestCase):
    """Test Access Security.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        self.content = self.root

    def test_modify(self):
        access = component.queryAdapter(self.content, IAccessSecurity)
        checkPermission = getSecurityManager().checkPermission

        for role, author_ok in [
            ('Authenticated', True),
            ('Viewer', True),
            ('Reader', True),
            ('Author', True),
            ('Editor', False),
            ('ChiefEditor', False),
            ('Manager', False)]:

            access.set_minimum_role(role)

            self.assertEqual(access.is_acquired(), False)
            self.assertEqual(access.acquired, False)
            self.assertEqual(access.get_minimum_role(), role)
            self.assertEqual(access.minimum_role, role)

            self.assertEqual(
                bool(checkPermission('View', self.content)), author_ok)

    def test_reset(self):
        """Test that set_acquired reset the settings.
        """
        access = component.queryAdapter(self.content, IAccessSecurity)
        access.set_minimum_role('Manager')

        access.set_acquired()
        self.assertEqual(access.is_acquired(), True)
        self.assertEqual(access.acquired, True)
        self.assertEqual(access.get_minimum_role(), None)
        self.assertEqual(access.minimum_role, None)

    def test_default(self):
        """Test default settings.
        """
        access = component.queryAdapter(self.content, IAccessSecurity)
        self.assertTrue(verifyObject(IAccessSecurity, access))

        # By default settings should acquire and no restriction shall be set.
        self.assertEqual(access.is_acquired(), True)
        self.assertEqual(access.acquired, True)
        self.assertEqual(access.get_minimum_role(), None)
        self.assertEqual(access.minimum_role, None)


class RootAccessSecurityTestCase(AccessSecurityTestCase):
    """Test Access Security.
    """
    layer = FunctionalLayer

    def setUp(self):
        super(RootAccessSecurityTestCase, self).setUp()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.content = self.root.folder



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AccessSecurityTestCase))
    suite.addTest(unittest.makeSuite(RootAccessSecurityTestCase))
    return suite
