# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Acquisition import aq_base
from AccessControl.SecurityManagement import newSecurityManager, \
    noSecurityManager, getSecurityManager
from Testing.ZopeTestCase import utils
from Testing import ZopeTestCase
import transaction
import zope.component.eventtesting

from Products.Silva.tests.layer import SilvaLayer, SilvaFunctionalLayer
from Products.Silva.tests.layer import user_name, user_password
from Products.Silva.tests.layer import users, setUp, tearDown

from StringIO import StringIO

user_manager = 'manager'
user_chiefeditor = 'chiefeditor'
user_editor = 'editor'
user_author = 'author'
user_reader = 'reader'
user_dummy = 'dummy'


class SilvaTestCase(ZopeTestCase.Sandboxed, ZopeTestCase.ZopeTestCase):

    layer = SilvaLayer

    def assertSame(self, first, second, msg=None):
        """Assert that first is the same same object than second,
        Acquisition wrapper removed. If the condition is not
        satisfied, the test will fail with the given msg if not None.
        """
        if msg is None:
            msg = u'%r is not %r' % (first, second)
        if aq_base(first) is not aq_base(second):
            raise self.failureException, msg

    def assertListEqual(self, first, second, msg=None):
        """Assert that the list first and second contains the same
        object, without paying attention to the order of the
        elements. If the condition is not satisfied, the test will
        fail with the given msg if not None.
        """
        c_first = list(first)
        c_first.sort()
        c_second = list(second)
        c_second.sort()
        if msg is None:
            msg = u'%r != %s' % (c_first, c_second)
        if not c_first == c_second:
            raise self.failureException, msg

    def get_users(self):
        """Return the list of the available list of test users.
        """
        return users.keys()

    def get_password(self, username):
        """Return the password of the given user.
        """
        return users[username]['password']

    def get_role(self, username):
        return users[username]['role']

    def get_user_by_role(self, role):
        for name, value in users.items():
            if value['role'] == role:
                return name

    def getRoot(self):
        """Returns the silva root object, i.e. the "fixture root".
           Override if you don't like the default.
        """
        return self.app.root

    @property
    def silva_url(self):
        """Return the absolute url of silva root.
        """
        return self.getRoot().absolute_url()

    def afterSetUp(self):
        '''Called after setUp() has completed. This is
           far and away the most useful hook.
        '''
        pass

    def beforeTearDown(self):
        '''Called before tearDown() is executed.
           Note that tearDown() is not called if
           setUp() fails.
        '''
        pass

    def afterClear(self):
        '''Called after the fixture has been cleared.
           Note that this is done during setUp() *and*
           tearDown().
        '''
        pass

    def beforeSetUp(self):
        '''Called before the ZODB connection is opened,
           at the start of setUp(). By default begins
           a new transaction.
        '''
        transaction.begin()

    def beforeClose(self):
        '''Called before the ZODB connection is closed,
           at the end of tearDown(). By default aborts
           the transaction.
        '''
        transaction.abort()

    def setUp(self):
        '''Sets up the fixture. Do not override,
           use the hooks instead.
        '''
        transaction.abort()
        self.beforeSetUp()
        try:
            self.app = self._app()
            setUp(self)
            self.silva = self.root = self.getRoot()
            self.catalog = self.silva.service_catalog
            self.login()
            self.app.REQUEST.AUTHENTICATED_USER=\
                self.app.acl_users.getUser(ZopeTestCase.user_name)
            self.afterSetUp()
        except:
            self.beforeClose()
            self._clear()
            raise

    def tearDown(self):
        '''Tears down the fixture. Do not override,
           use the hooks instead.
        '''
        self.beforeTearDown()
        self._clear(1)

    def _clear(self, call_close_hook=0):
        '''Clears the fixture.'''
        try:
            if call_close_hook:
                self.beforeClose()
        finally:
            tearDown(self)
            self._close()
            self.afterClear()

    def _close(self):
        '''Closes the ZODB connection.'''
        super(SilvaTestCase, self)._close()

    def addObject(self, container, type_name, id, product='Silva', **kw):
        getattr(container.manage_addProduct[product],
            'manage_add%s' % type_name)(id, **kw)
        # gives the new object a _p_jar ...
        transaction.savepoint()
        return getattr(container, id)

    # Security interfaces

    def setRoles(self, roles, name=user_name):
        '''Changes the roles assigned to a user.'''
        uf = self.root.acl_users
        uf._doChangeUser(name, None, roles, [])
        if name == getSecurityManager().getUser().getId():
            self.login(name)

    def setPermissions(self, permissions, role='Member', context=None):
        '''Changes the permissions assigned to a role.
           If context is None it defaults to the root
           object.
        '''
        if context is None:
            context = self.root
        context.manage_role(role, permissions)

    def installExtension(self, extension):
        """Installs a Silva extension"""
        ZopeTestCase.installProduct(extension)
        self.getRoot().service_extensions.install(extension)

    def login(self, name=user_name):
        '''Logs in as the specified user.'''
        uf = self.root.acl_users
        user = uf.getUserById(name).__of__(uf)
        newSecurityManager(None, user)

    def logout(self):
        '''Logs out.'''
        noSecurityManager()

    def add_folder(self, object, id, title, **kw):
        return self.addObject(object, 'Folder', id, title=title, **kw)

    def add_publication(self, object, id, title, **kw):
        return self.addObject(object, 'Publication', id, title=title, **kw)

    def add_document(self, object, id, title):
        return self.addObject(object, 'Document', id, title=title,
                              product='SilvaDocument')

    def add_ghost(self, object, id, content_url):
        return self.addObject(object, 'Ghost', id, content_url=content_url)

    def add_link(self, object, id, title, url):
        return self.addObject(object, 'Link', id, title=title, url=url)

    def add_image(self, object, id, title, **kw):
        return self.addObject(object, 'Image', id, title=title, **kw)

    def add_file(self, object, id, title, **kw):
        return self.addObject(object, 'File', id, title=title, **kw)

    def add_find(self, object, id, title):
        return self.addObject(object, 'SilvaFind', id, title=title, product='SilvaFind')

    def get_events(self, event_type=None, filter=None):
        """Return events that were fired since the beginning of the
        test, which includes events fired in the `afterSetUp` method.
        """
        return zope.component.eventtesting.getEvents(event_type, filter)

    def clear_events(self):
        zope.component.eventtesting.clearEvents()


class SilvaFileTestCase(SilvaTestCase):
    """Test case which keep the result of the request (to test files).
    """

    def _app(self):
        app = super(SilvaFileTestCase, self)._app()
        self.request_out = StringIO()
        return utils.makerequest(app.aq_base, self.request_out)

    def get_request_data(self):
        content = self.request_out.getvalue()
        self.request_out.seek(0)
        self.request_out.truncate()
        if content.startswith('Status: 200'):
            content = content[content.find('\r\n\r\n')+4:]
        return content


class SilvaFunctionalTestCase(ZopeTestCase.FunctionalTestCase, SilvaTestCase):
    """Base class for functional tests.
    """

    layer = SilvaFunctionalLayer


