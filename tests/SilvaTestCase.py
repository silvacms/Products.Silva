# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

__version__ = '0.3.1'

from Testing.ZopeTestCase import utils, connections, sandbox, ZopeLite
from Testing import ZopeTestCase
from ZODB.blob import BlobStorage
from ZODB.DemoStorage import DemoStorage
import ZODB

from StringIO import StringIO

import tempfile, shutil
import transaction
import zope.component.eventtesting
from zope.interface import Interface
from zope.app.component.hooks import setSite

user_manager = 'manager'
user_chiefeditor = 'chiefeditor'
user_editor = 'editor'
user_author = 'author'
user_reader = 'reader'
user_dummy = 'dummy'

from AccessControl.SecurityManagement import newSecurityManager, \
    noSecurityManager, getSecurityManager

import helpers
from layer import SilvaLayer, SilvaFunctionalLayer
from layer import user_name, user_password, users, setUp, tearDown


class ISilvaTestBlobs(Interface):
    """This test needs blobs.
    """

class SilvaTestCase(ZopeTestCase.Sandboxed, ZopeTestCase.ZopeTestCase):
    layer = SilvaLayer

    _blob_dir = None

    def get_users(self):
        return users.keys()

    def get_password(self, username):
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
            setSite(self.silva)
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

    def _app(self):
        """Returns the app object for a test.
        """
        # Testing sucks and defined a STUPID quota of 1Mo. Change it
        # to 32Mo. Add support for blob tests as well.
        import Zope2
        storage = DemoStorage(base=Zope2.DB._storage, quota=1<<25)
        connection = ZODB.DB(storage).open()
        if ISilvaTestBlobs.providedBy(self):
            self._blob_dir = tempfile.mkdtemp('-blobs')
            connection = ZODB.DB(BlobStorage(self._blob_dir, connection._storage)).open()
        app = ZopeLite.app(connection)
        sandbox.AppZapper().set(app)
        app = utils.makerequest(app)
        connections.register(app)
        return app

    def _clear(self, call_close_hook=0):
        '''Clears the fixture.'''
        try:
            if call_close_hook:
                self.beforeClose()
        finally:
            self._close()
            self.logout()
            self.afterClear()

    def _close(self):
        '''Closes the ZODB connection.'''
        super(SilvaTestCase, self)._close()
        if self._blob_dir:
            shutil.rmtree(self._blob_dir)
            self._blob_dir = None

    def addObject(self, container, type_name, id, product='Silva',
            **kw):
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
        app = app.aq_base
        request_out = self.request_out = StringIO()
        return utils.makerequest(app, request_out)

    def get_request_data(self, data):
        if data:
            if hasattr(data, 'next'):
                s = data._stream.read()
            else:
                s = data
        else:
            s = self.request_out.getvalue()
            self.request_out.seek(0)
            self.request_out.truncate()
        if s.startswith('Status: 200'):
            s = s[s.find('\n\n')+2:]
        return s


class SilvaFunctionalTestCase(ZopeTestCase.FunctionalTestCase, SilvaTestCase):
    """Base class for functional tests.
    """

    layer = SilvaFunctionalLayer


