# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import IAccessSecurity
from silva.core.interfaces import IAuthorization, IAuthorizationManager
from silva.core.interfaces import UnauthorizedRoleAssignement
from silva.core.services.interfaces import IMemberService
from zope import component
from zope.interface.verify import verifyObject

from AccessControl import getSecurityManager
from Products.Silva.Security.management import is_role_greater_or_equal
from Products.Silva.Security.management import is_role_greater
from Products.Silva.testing import FunctionalLayer
from Products.Silva.testing import assertNotTriggersEvents, assertTriggersEvents


class UtilitiesTestCase(unittest.TestCase):

    def test_role_greater(self):
        self.assertFalse(is_role_greater('Editor', 'Manager'))
        self.assertFalse(is_role_greater('Reader', 'Editor'))
        self.assertFalse(is_role_greater('Viewer', 'Reader'))
        self.assertFalse(is_role_greater('Editor', 'Editor'))
        self.assertTrue(is_role_greater('Editor', 'Reader'))
        self.assertTrue(is_role_greater('Manager', 'Editor'))
        self.assertFalse(is_role_greater('Chinese', 'Editor'))

    def test_role_greater_or_equal(self):
        self.assertFalse(is_role_greater_or_equal('Editor', 'Manager'))
        self.assertFalse(is_role_greater_or_equal('Reader', 'Editor'))
        self.assertFalse(is_role_greater_or_equal('Viewer', 'Reader'))
        self.assertTrue(is_role_greater_or_equal('Editor', 'Editor'))
        self.assertTrue(is_role_greater_or_equal('Manager', 'Manager'))
        self.assertTrue(is_role_greater_or_equal('Manager', 'Editor'))
        self.assertFalse(is_role_greater_or_equal('Chinese', 'Editor'))


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

            with assertTriggersEvents('SecurityRestrictionModifiedEvent'):
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
        with assertTriggersEvents('SecurityRestrictionModifiedEvent'):
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
        with assertTriggersEvents('SecurityRestrictionModifiedEvent'):
            access.set_minimum_role('Manager')
        checkPermission = getSecurityManager().checkPermission
        self.assertEqual(bool(checkPermission('View', self.content)), False)

        with assertTriggersEvents('SecurityRestrictionModifiedEvent'):
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

    def test_interface(self):
        access = IAuthorizationManager(self.root.folder)
        self.assertTrue(verifyObject(IAuthorizationManager, access))

    def test_logged_in_user(self):
        """Lookup information about the current logged in user.
        """
        for user_id in ['viewer', 'reader', 'author', 'editor', 'manager']:
            # Test users have the same login than their role (in lower case).
            self.layer.login(user_id)
            access = IAuthorizationManager(self.root.folder)
            self.assertEqual(access.get_user_role().lower(), user_id)

            authorization = access.get_authorization()
            self.assertTrue(verifyObject(IAuthorization, authorization))
            self.assertEqual(authorization.identifier, user_id)
            self.assertEqual(authorization.role.lower(), user_id)
            self.assertEqual(authorization.type, 'user')
            self.assertEqual(authorization.email, None)
            # By default users don't have a local here. Their role is
            # acquired.
            self.assertEqual(authorization.local_role, None)
            self.assertEqual(authorization.acquired_role.lower(), user_id)

    def test_user_lookup(self):
        """Lookup information about one specific user.
        """
        for user_id in ['viewer', 'reader', 'author', 'editor', 'manager']:
            # Test users have the same login than their role (in lower case).
            access = IAuthorizationManager(self.root.folder)
            self.assertEqual(
                access.get_user_role(user_id).lower(), user_id)

            authorization = access.get_authorization(user_id)
            self.assertTrue(verifyObject(IAuthorization, authorization))
            self.assertEqual(authorization.identifier, user_id)
            self.assertEqual(authorization.role.lower(), user_id)
            # By default users don't have a local here. Their role is
            # acquired.
            self.assertEqual(authorization.local_role, None)
            self.assertEqual(authorization.acquired_role.lower(), user_id)

    def test_user_no_default_role(self):
        """Lookup a user that doesn't have a default role.
        """
        access = IAuthorizationManager(self.root.folder)
        self.assertEqual(access.get_user_role('dummy'), None)

        authorization = access.get_authorization('dummy')
        self.assertTrue(verifyObject(IAuthorization, authorization))
        self.assertEqual(authorization.identifier, 'dummy')
        self.assertEqual(authorization.type, 'user')
        self.assertEqual(authorization.role, None)
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, None)

    def test_grant_role(self):
        """Test setting a role (as a ChiefEditor).
        """
        access = IAuthorizationManager(self.root.folder)
        authorization = access.get_authorization('reader')
        self.assertEqual(authorization.role, 'Reader')

        # We (chiefeditor) don't have Manager, so can't give that role.
        with assertNotTriggersEvents('SecurityRoleAddedEvent'):
            with self.assertRaises(UnauthorizedRoleAssignement):
                authorization.grant('Manager')

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

        access = IAuthorizationManager(self.root.folder)
        authorization = access.get_authorization('reader')
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
        authorization = access.get_authorization('reader')
        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.role, 'Manager')

    def test_grant_role_as_nobody(self):
        """Test setting a role while being nobody.
        """
        self.layer.login('dummy')

        access = IAuthorizationManager(self.root.folder)
        authorization = access.get_authorization('reader')
        self.assertEqual(authorization.role, 'Reader')

        # You don't have the right to do any of those
        with assertNotTriggersEvents('SecurityRoleAddedEvent'):
            with self.assertRaises(UnauthorizedRoleAssignement):
                authorization.grant('Manager')
            with self.assertRaises(UnauthorizedRoleAssignement):
                authorization.grant('Editor')
            with self.assertRaises(UnauthorizedRoleAssignement):
                authorization.grant('Author')

            # The user already have role, reader, so this does nothing
            self.assertEqual(authorization.grant('Viewer'), False)

        # Nothing changed
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.role, 'Reader')

    def test_authorization_email_user(self):
        """ Test email property on authorization object.
        """
        member_service = component.getUtility(IMemberService)
        member = member_service.get_member('viewer')
        member.set_email('viewer@silva.org')

        access = IAuthorizationManager(self.root.folder)
        authorization = access.get_authorization('viewer')
        self.assertEqual('viewer@silva.org', authorization.email)
        authorization = access.get_authorization('reader')
        self.assertEqual(None, authorization.email)


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
        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.folder = self.root.publication.folder

        access = IAuthorizationManager(self.root)
        authorization = access.get_authorization('reader')
        authorization.grant('Editor')
        authorization = access.get_authorization('viewer')
        authorization.grant('Reader')

        access = IAuthorizationManager(self.root.publication)
        authorization = access.get_authorization('viewer')
        authorization.grant('ChiefEditor')

        access = IAuthorizationManager(self.folder)
        authorization = access.get_authorization('reader')
        authorization.grant('Manager')

    def test_get_defined_authorizations(self):
        """Retrieve all current authorization, trying to acquire.
        """
        access = IAuthorizationManager(self.folder)

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
        access = IAuthorizationManager(self.folder)

        authorizations = access.get_defined_authorizations(dont_acquire=True)
        self.assertEqual(len(authorizations), 1)
        self.assertTrue('reader' in authorizations.keys())

        authorization = authorizations['reader']
        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.acquired_role, None)
        self.assertEqual(authorization.role, 'Manager')

    def test_get_authorization_dont_acquire(self):
        """Retrieve a user authorization that have some acquired roles.
        """
        access = IAuthorizationManager(self.folder)

        authorization = access.get_authorization(
            'reader', dont_acquire=True)
        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.acquired_role, None)
        self.assertEqual(authorization.role, 'Manager')

        authorization = access.get_authorization(
            'viewer', dont_acquire=True)
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, None)
        self.assertEqual(authorization.role, None)

    def  test_get_users_authorization(self):
        """Test get_authorizations.
        """
        access = IAuthorizationManager(self.folder)

        authorizations = access.get_authorizations(
            ['reader', 'viewer', 'editor', 'hacker'])
        self.assertEqual(len(authorizations), 3)
        self.assertTrue('reader' in authorizations.keys())
        self.assertTrue('viewer' in authorizations.keys())
        self.assertTrue('editor' in authorizations.keys())
        self.assertFalse('manager' in authorizations.keys())
        self.assertFalse('hacker' in authorizations.keys())

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
        access = IAuthorizationManager(self.folder)
        authorization = access.get_authorization('reader')

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
        authorization = access.get_authorization('reader')
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, 'Editor')
        self.assertEqual(authorization.role, 'Editor')

    def test_revoke_as_chiefeditor_unauthorized(self):
        """Try to revoke a manager local role as a chiefeditor.
        """
        self.layer.login('chiefeditor')

        access = IAuthorizationManager(self.folder)
        authorization = access.get_authorization('reader')

        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.acquired_role, 'Editor')
        self.assertEqual(authorization.role, 'Manager')

        # We don't have the right to revoke that role
        with assertNotTriggersEvents('SecurityRoleRemovedEvent'):
            with self.assertRaises(UnauthorizedRoleAssignement):
                authorization.revoke()

        # So it is not changed
        self.assertEqual(authorization.local_role, 'Manager')
        self.assertEqual(authorization.acquired_role, 'Editor')
        self.assertEqual(authorization.role, 'Manager')

    def test_revoke_own_role_as_chiefeditor(self):
        """Revoke its own local role as chiefeditor.
        """
        self.layer.login('viewer')

        access = IAuthorizationManager(self.root.publication)
        authorization = access.get_authorization('viewer')

        self.assertEqual(authorization.local_role, 'ChiefEditor')
        self.assertEqual(authorization.acquired_role, 'Reader')
        self.assertEqual(authorization.role, 'ChiefEditor')

        # We try to revoke the role
        with assertNotTriggersEvents('SecurityRoleRemovedEvent'):
            with self.assertRaises(UnauthorizedRoleAssignement):
                authorization.revoke()

        self.assertEqual(authorization.local_role, 'ChiefEditor')
        self.assertEqual(authorization.acquired_role, 'Reader')
        self.assertEqual(authorization.role, 'ChiefEditor')

    def test_revoke_as_chiefeditor(self):
        """Revoke a local role as a chiefeditor (of an editor).
        """
        self.layer.login('chiefeditor')

        access = IAuthorizationManager(self.root)
        authorization = access.get_authorization('reader')

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
        authorization = access.get_authorization('reader')
        self.assertEqual(authorization.local_role, None)
        self.assertEqual(authorization.acquired_role, 'Reader')
        self.assertEqual(authorization.role, 'Reader')

    def test_revoke_as_nobody(self):
        """Revoke local roles as nobody.
        """
        self.layer.login('dummy')

        access = IAuthorizationManager(self.root)
        # We don't have the right to revoke that role
        authorization = access.get_authorization('reader')
        with assertNotTriggersEvents('SecurityRoleRemovedEvent'):
            with self.assertRaises(UnauthorizedRoleAssignement):
                authorization.revoke()

        # We don't have the right to revoke that role
        authorization = access.get_authorization('viewer')
        with assertNotTriggersEvents('SecurityRoleRemovedEvent'):
            with self.assertRaises(UnauthorizedRoleAssignement):
                authorization.revoke()

    def test_revoke_no_role(self):
        """Revoke local role when there is no local role.
        """
        access = IAuthorizationManager(self.folder)
        authorization = access.get_authorization('viewer')

        self.assertEqual(authorization.local_role, None)

        with assertNotTriggersEvents('SecurityRoleRemovedEvent'):
            self.assertEqual(authorization.revoke(), False)

        self.assertEqual(authorization.local_role, None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UtilitiesTestCase))
    suite.addTest(unittest.makeSuite(AccessSecurityTestCase))
    suite.addTest(unittest.makeSuite(RootAccessSecurityTestCase))
    suite.addTest(unittest.makeSuite(UserAccessSecurityTestCase))
    suite.addTest(unittest.makeSuite(AcquiredUserAccessSecurityTestCase))
    return suite
