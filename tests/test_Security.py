# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core.interfaces import IAccessSecurity, IUserAccessSecurity
from silva.core.interfaces import IUserAuthorization
from zope import component
from zope.interface.verify import verifyObject

from AccessControl import getSecurityManager
from Products.Silva.testing import FunctionalLayer
from Products.Silva.testing import assertNotTriggersEvents, assertTriggersEvents
from Products.Silva.Security import UnauthorizedRoleAssignement


class AccessSecurityTestCase(unittest.TestCase):
    """Test Access Security.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.content = self.root.folder

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

    def test_acquire(self):
        """Test that children content acquire correctly the settings
        from parents.
        """
        access = component.queryAdapter(self.content, IAccessSecurity)
        access.set_minimum_role('ChiefEditor')
        checkPermission = getSecurityManager().checkPermission
        self.assertEqual(
            bool(checkPermission('View', self.content)), False)

        children = self.root.folder.folder
        children_access = component.queryAdapter(children, IAccessSecurity)
        self.assertEqual(children_access.is_acquired(), True)
        self.assertEqual(children_access.acquired, True)
        self.assertEqual(children_access.get_minimum_role(), 'ChiefEditor')
        self.assertEqual(children_access.minimum_role, 'ChiefEditor')
        self.assertEqual(bool(checkPermission('View', children)), False)

    def test_reset(self):
        """Test that set_acquired reset the settings.
        """
        access = component.queryAdapter(self.content, IAccessSecurity)
        access.set_minimum_role('Manager')
        checkPermission = getSecurityManager().checkPermission
        self.assertEqual(bool(checkPermission('View', self.content)), False)

        access.set_acquired()
        self.assertEqual(access.is_acquired(), True)
        self.assertEqual(access.acquired, True)
        self.assertEqual(access.get_minimum_role(), None)
        self.assertEqual(access.minimum_role, None)
        self.assertEqual(bool(checkPermission('View', self.content)), True)

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

    def setUp(self):
        super(RootAccessSecurityTestCase, self).setUp()
        self.content = self.root


class UserAccessSecurityTestCase(unittest.TestCase):
    """Test user access security adapter.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('chiefeditor')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

        self.access = component.queryAdapter(
            self.root.folder, IUserAccessSecurity)

    def test_interface(self):
        self.assertTrue(verifyObject(IUserAccessSecurity, self.access))

    def test_logged_in_user(self):
        """Lookup information about the current logged in user.
        """
        for user_id in ['viewer', 'reader', 'author', 'editor', 'manager']:
            # Test users have the same login than their role (in lower case).
            self.layer.login(user_id)
            self.assertEqual(
                self.access.get_user_role().lower(),
                user_id)

            authorization = self.access.get_user_authorization()
            self.assertTrue(verifyObject(IUserAuthorization, authorization))
            self.assertEqual(authorization.userid, user_id)
            self.assertEqual(authorization.role.lower(), user_id)
            # By default users don't have a local here. Their role is
            # acquired.
            self.assertEqual(authorization.local_role, None)
            self.assertEqual(authorization.acquired_role.lower(), user_id)

    def test_user_lookup(self):
        """Lookup information about one specific user.
        """
        for user_id in ['viewer', 'reader', 'author', 'editor', 'manager']:
            # Test users have the same login than their role (in lower case).
            self.assertEqual(
                self.access.get_user_role(user_id).lower(),
                user_id)

            authorization = self.access.get_user_authorization(user_id)
            self.assertTrue(verifyObject(IUserAuthorization, authorization))
            self.assertEqual(authorization.userid, user_id)
            self.assertEqual(authorization.role.lower(), user_id)
            # By default users don't have a local here. Their role is
            # acquired.
            self.assertEqual(authorization.local_role, None)
            self.assertEqual(authorization.acquired_role.lower(), user_id)

    def test_user_no_default_role(self):
        """Lookup a user that doesn't have a default role.
        """
        self.assertEqual(self.access.get_user_role('dummy'), None)

        authorization = self.access.get_user_authorization('dummy')
        self.assertTrue(verifyObject(IUserAuthorization, authorization))
        self.assertEqual(authorization.userid, 'dummy')
        self.assertEqual(authorization.role, None)
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, None)

    def test_grant_role(self):
        """Test setting a role (as a ChiefEditor).
        """
        authorization = self.access.get_user_authorization('reader')
        self.assertEqual(authorization.role, 'Reader')

        # We (chiefeditor) don't have Manager, so can't give that role.
        with assertNotTriggersEvents('SecurityRoleAddedEvent'):
            self.assertRaises(
                UnauthorizedRoleAssignement,
                authorization.grant,
                'Manager')

        # The user already have role, reader, so this does nothing
        with assertNotTriggersEvents('SecurityRoleAddedEvent'):
            self.assertEqual(authorization.grant('Viewer'), False)
        self.assertEqual(authorization.local_role, None)

        # The user doesn't have that role so it is set
        with assertTriggersEvents('SecurityRoleAddedEvent'):
            self.assertEqual(authorization.grant('Editor'), True)
        self.assertEqual(authorization.local_role, 'Editor')

        # Now the user is editor
        self.assertEqual(authorization.role, 'Editor')

    def test_grant_role_as_manager(self):
        """Test setting a role (as a Manager).
        """
        self.layer.login('manager')

        authorization = self.access.get_user_authorization('reader')
        self.assertEqual(authorization.role, 'Reader')

        # The user already have role, reader, so this does nothing
        with assertNotTriggersEvents('SecurityRoleAddedEvent'):
            self.assertEqual(authorization.grant('Reader'), False)
        self.assertEqual(authorization.local_role, None)

        # The user doesn't have that role so it is set
        with assertTriggersEvents('SecurityRoleAddedEvent'):
            self.assertEqual(authorization.grant('Manager'), True)
        self.assertEqual(authorization.local_role, 'Manager')

        # Now the user is editor
        self.assertEqual(authorization.role, 'Manager')

        # A new query returns the same  results
        authorization = self.access.get_user_authorization('reader')
        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.role, 'Manager')

    def test_grant_role_as_nobody(self):
        """Test setting a role while being nobody.
        """
        self.layer.login('dummy')

        authorization = self.access.get_user_authorization('reader')
        self.assertEqual(authorization.role, 'Reader')

        # You don't have the right to do any of those
        with assertNotTriggersEvents('SecurityRoleAddedEvent'):
            self.assertRaises(
                UnauthorizedRoleAssignement,
                authorization.grant,
                'Manager')
            self.assertRaises(
                UnauthorizedRoleAssignement,
                authorization.grant,
                'Editor')
            self.assertRaises(
                UnauthorizedRoleAssignement,
                authorization.grant,
                'Author')

            # The user already have role, reader, so this does nothing
            self.assertEqual(authorization.grant('Viewer'), False)

        # Nothing changed
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.role, 'Reader')



class AcquiredUserAccessSecurityTestCase(unittest.TestCase):
    """Test user access security adapter when settings are acquired.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addPublication('publication', 'Publication')
        self.publication = self.root.publication
        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.folder = self.root.publication.folder

        access = IUserAccessSecurity(self.root)
        authorization = access.get_user_authorization('reader')
        authorization.grant('Editor')
        authorization = access.get_user_authorization('viewer')
        authorization.grant('Reader')

        access = IUserAccessSecurity(self.publication)
        authorization = access.get_user_authorization('viewer')
        authorization.grant('ChiefEditor')

        access = IUserAccessSecurity(self.folder)
        authorization = access.get_user_authorization('reader')
        authorization.grant('Manager')

    def test_get_defined_authorizations(self):
        """Retrieve all current authorization, trying to acquire.
        """
        access = IUserAccessSecurity(self.folder)

        authorizations = access.get_defined_authorizations()
        self.assertEqual(len(authorizations), 2)
        self.assertTrue('viewer' in authorizations.keys())
        self.assertTrue('reader' in authorizations.keys())

        authorization = authorizations['viewer']
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, 'ChiefEditor')
        self.assertEqual(authorization.role, 'ChiefEditor')

        authorization = authorizations['reader']
        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.acquired_role, 'Editor')
        self.assertEqual(authorization.role, 'Manager')

    def test_get_defined_authorizations_dont_acquire(self):
        """Retrieve current all current authorizations without acquiring.
        """
        access = IUserAccessSecurity(self.folder)

        authorizations = access.get_defined_authorizations(dont_acquire=True)
        self.assertEqual(len(authorizations), 1)
        self.assertTrue('reader' in authorizations.keys())

        authorization = authorizations['reader']
        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.acquired_role, None)
        self.assertEqual(authorization.role, 'Manager')

    def test_get_user_authorization_dont_acquire(self):
        """Retrieve a user authorization that have some acquired roles.
        """
        access = IUserAccessSecurity(self.folder)

        authorization = access.get_user_authorization(
            'reader', dont_acquire=True)
        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.acquired_role, None)
        self.assertEqual(authorization.role, 'Manager')

        authorization = access.get_user_authorization(
            'viewer', dont_acquire=True)
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, None)
        self.assertEqual(authorization.role, None)

    def  test_get_users_authorzation(self):
        """Test get_users_authorization.
        """
        access = IUserAccessSecurity(self.folder)

        authorizations = access.get_users_authorization(
            ['reader', 'viewer', 'editor'])
        self.assertEqual(len(authorizations), 3)
        self.assertTrue('reader' in authorizations.keys())
        self.assertTrue('viewer' in authorizations.keys())
        self.assertTrue('editor' in authorizations.keys())
        self.assertFalse('manager' in authorizations.keys())

        authorization = authorizations['reader']
        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.acquired_role, 'Editor')
        self.assertEqual(authorization.role, 'Manager')

        authorization = authorizations['editor']
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, 'Editor')
        self.assertEqual(authorization.role, 'Editor')


    def test_revoke_as_manager(self):
        """Revoke a local role as a manager.
        """
        access = IUserAccessSecurity(self.folder)
        authorization = access.get_user_authorization('reader')

        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.acquired_role, 'Editor')
        self.assertEqual(authorization.role, 'Manager')

        # We revoke the role
        with assertTriggersEvents('SecurityRoleRemovedEvent'):
            self.assertEqual(authorization.revoke(), True)

        # It is gone
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, 'Editor')
        self.assertEqual(authorization.role, 'Editor')

        # Even on a new query
        authorization = access.get_user_authorization('reader')
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, 'Editor')
        self.assertEqual(authorization.role, 'Editor')

    def test_revoke_as_chiefeditor_unauthorized(self):
        """Try to revoke a manager local role as a chiefeditor.
        """
        self.layer.login('chiefeditor')

        access = IUserAccessSecurity(self.folder)
        authorization = access.get_user_authorization('reader')

        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.acquired_role, 'Editor')
        self.assertEqual(authorization.role, 'Manager')

        # We don't have the right to revoke that role
        with assertNotTriggersEvents('SecurityRoleRemovedEvent'):
            self.assertRaises(
                UnauthorizedRoleAssignement,
                authorization.revoke)

        # So it is not changed
        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.acquired_role, 'Editor')
        self.assertEqual(authorization.role, 'Manager')

    def test_revoke_as_chiefeditor(self):
        """Revoke a local role as a chiefeditor (of an editor).
        """
        self.layer.login('chiefeditor')

        access = IUserAccessSecurity(self.root)
        authorization = access.get_user_authorization('reader')

        self.assertEqual(authorization.local_role, 'Editor')
        self.assertEqual(authorization.acquired_role, 'Reader')
        self.assertEqual(authorization.role, 'Editor')

        # We revoke the role
        with assertTriggersEvents('SecurityRoleRemovedEvent'):
            self.assertEqual(authorization.revoke(), True)

        # It is gone
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, 'Reader')
        self.assertEqual(authorization.role, 'Reader')

        # Even on a new query
        authorization = access.get_user_authorization('reader')
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, 'Reader')
        self.assertEqual(authorization.role, 'Reader')

    def test_revoke_as_nobody(self):
        """Revoke local roles as nobody.
        """
        self.layer.login('dummy')

        access = IUserAccessSecurity(self.root)
        # We don't have the right to revoke that role
        authorization = access.get_user_authorization('reader')
        with assertNotTriggersEvents('SecurityRoleRemovedEvent'):
            self.assertRaises(
                UnauthorizedRoleAssignement,
                authorization.revoke)

        # We don't have the right to revoke that role
        authorization = access.get_user_authorization('viewer')
        with assertNotTriggersEvents('SecurityRoleRemovedEvent'):
            self.assertRaises(
                UnauthorizedRoleAssignement,
                authorization.revoke)

    def test_revoke_no_role(self):
        """Revoke local role when there is no local role.
        """
        access = IUserAccessSecurity(self.folder)
        authorization = access.get_user_authorization('viewer')

        self.assertEqual(authorization.local_role, None)

        with assertNotTriggersEvents('SecurityRoleRemovedEvent'):
            self.assertEqual(authorization.revoke(), False)

        self.assertEqual(authorization.local_role, None)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AccessSecurityTestCase))
    suite.addTest(unittest.makeSuite(RootAccessSecurityTestCase))
    suite.addTest(unittest.makeSuite(UserAccessSecurityTestCase))
    suite.addTest(unittest.makeSuite(AcquiredUserAccessSecurityTestCase))
    return suite
