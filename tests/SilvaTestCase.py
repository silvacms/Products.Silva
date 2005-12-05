#
# SilvaTestCase
#

__version__ = '0.3.1'

from Testing import ZopeTestCase

import transaction

user_name = ZopeTestCase.user_name
ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('TemporaryFolder')
ZopeTestCase.installProduct('ZCTextIndex')
ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('PageTemplates')
ZopeTestCase.installProduct('Formulator')
ZopeTestCase.installProduct('FileSystemSite')
ZopeTestCase.installProduct('ParsedXML')
ZopeTestCase.installProduct('XMLWidgets')
ZopeTestCase.installProduct('ProxyIndex')
try:
    # if available, it is installed by Silva.install.installSubscriptions
    from Products.MaildropHost import MaildropHost
    ZopeTestCase.installProduct('MaildropHost')    
except ImportError:
    pass

ZopeTestCase.installProduct('SilvaMetadata')
ZopeTestCase.installProduct('SilvaViews')
if ZopeTestCase.hasProduct('SilvaExternalSources'):
    ZopeTestCase.installProduct('SilvaExternalSources')
ZopeTestCase.installProduct('SilvaDocument')
ZopeTestCase.installProduct('Silva')

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager, getSecurityManager
from AccessControl.User import User

from Acquisition import aq_base
import time

from zope.app.tests import placelesssetup

class SilvaTestCase(ZopeTestCase.ZopeTestCase):

    _configure_root = 1

    def getRoot(self):
        """Returns the silva root object, i.e. the "fixture root". 
           Override if you don't like the default.
        """
        return self.app.root

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
        noSecurityManager()
        self.beforeSetUp()
        # BBB should be able to remove this in Zope 2.9
        placelesssetup.setUp()
        try:
            self.app = self._app()
            self.silva = self.root = self.getRoot()
            self.catalog = self.silva.service_catalog
            if self._configure_root:
                self._setupRootUser()
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
        # BBB should be able to remove this in Zope 2.9
        placelesssetup.tearDown()
        
    def _app(self):
        '''Returns the app object for a test.'''
        return ZopeTestCase.app()

    def _setupRootUser(self):
        '''Creates the root user.'''
        uf = self.root.acl_users
        uf._doAddUser(user_name, 'secret', ['ChiefEditor'], [])

    def _clear(self, call_close_hook=0):
        '''Clears the fixture.'''
        try:
            if self._configure_root:
                # This is paranoia mostly as the transaction
                # should be aborted anyway...
                try: self.root.acl_users._doDelUsers([user_name])
                except: pass
                try: self.root.Members._delObject(user_name)
                except: pass
            if call_close_hook:
                self.beforeClose()
        finally:
            self._close()
            self.logout()
            self.afterClear()

    def _close(self):
        '''Closes the ZODB connection.'''
        ZopeTestCase.close(self.app)
        
    def addObject(self, container, type_name, id, product='Silva',
            **kw):
        getattr(container.manage_addProduct[product],
            'manage_add%s' % type_name)(id, **kw)
        # gives the new object a _p_jar ...
        transaction.get().commit(1)
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

def setupSilvaRoot(app, id='root', quiet=0):
    '''Creates a Silva root.'''
    if not hasattr(aq_base(app), id):
        _start = time.time()
        if not quiet:
            ZopeTestCase._print('Adding Silva Root... ')
        uf = app.acl_users
        uf._doAddUser('SilvaTestCase', '', ['Manager'], [])
        user = uf.getUserById('SilvaTestCase').__of__(uf)
        newSecurityManager(None, user)
        factory = app.manage_addProduct['TemporaryFolder']
        factory.constructTemporaryFolder('temp_folder', '')
        factory = app.manage_addProduct['Silva']
        factory.manage_addRoot(id, '')
        root = app.root
        noSecurityManager()
        transaction.commit()
        if not quiet:
            ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

# Create a Silva site in the test (demo-) storage
app = ZopeTestCase.app()
setupSilvaRoot(app, id='root')
transaction.commit()
ZopeTestCase.close(app)
