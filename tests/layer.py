# -*- coding: utf-8 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import time

# Zope 3
import zope.component.eventtesting
from zope.component import provideHandler
from zope.testing.cleanup import cleanUp as _cleanUp

# Zope 2
from Acquisition import aq_base
from Testing import ZopeTestCase
from Testing.ZopeTestCase.layer import ZopeLiteLayer
from AccessControl.SecurityManagement import newSecurityManager, \
    noSecurityManager
import transaction

# Install Zope 2 Products

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

from Products.Silva import MAILDROPHOST_AVAILABLE
if  MAILDROPHOST_AVAILABLE:
    # if available, it is installed by Silva.install.installSubscriptions
    ZopeTestCase.installProduct('MaildropHost')    

ZopeTestCase.installProduct('Groups')
ZopeTestCase.installProduct('SilvaFind')
ZopeTestCase.installProduct('SilvaMetadata')
ZopeTestCase.installProduct('SilvaViews')
if ZopeTestCase.hasProduct('SilvaExternalSources'):
    ZopeTestCase.installProduct('SilvaExternalSources')
ZopeTestCase.installProduct('SilvaDocument')
ZopeTestCase.installProduct('Silva')
ZopeTestCase.installProduct('Five')
ZopeTestCase.installPackage('silva.core.views')
ZopeTestCase.installPackage('silva.core.layout')

user_name = ZopeTestCase.user_name
user_password = ZopeTestCase.user_password

# Default silva test user and password
users = {
    'manager': {'password': ZopeTestCase.user_password,
                'role': 'Manager' },
    'chiefeditor': {'password': ZopeTestCase.user_password,
                    'role': 'ChiefEditor' },
    'editor': {'password': ZopeTestCase.user_password,
               'role': 'Editor' },
    'author': {'password': ZopeTestCase.user_password,
               'role': 'Author' },
    'reader': {'password': ZopeTestCase.user_password,
               'role': 'Reader' },
    'dummy': {'password': ZopeTestCase.user_password,
              'role': '' },
}


def setDebugMode(mode):
    """Allows manual setting of Five's inspection of debug mode to
    allow for zcml to fail meaningfully.
    """
    import Products.Five.fiveconfigure as fc
    fc.debug_mode = mode

def cleanUp():
    """Clean up component architecture.
    """
    _cleanUp()
    import Products.Five.zcml as zcml
    zcml._initialized = 0

def setupRootUser(app):
    """Creates all test users.
    """
    uf = app.root.acl_users
    # original
    uf._doAddUser(user_name, user_password, ['ChiefEditor'], [])

    for username, info in users.items():
        uf._doAddUser(username, info['password'], [info['role']], [])

def setupSilvaRoot(app):
    """Creates a Silva root.
    """
    _start = time.time()
    uf = app.acl_users
    uf._doAddUser('SilvaTestCase', '', ['Manager'], [])
    user = uf.getUserById('SilvaTestCase').__of__(uf)
    newSecurityManager(None, user)
    ZopeTestCase.utils.setupCoreSessions(app)
    app.manage_addProduct['Silva'].manage_addRoot('root', '')
    noSecurityManager()

def setupSilva():
    """Create a Silva site in the test (demo-) storage.
    """
    app = ZopeTestCase.app()
    setupSilvaRoot(app)
    setupRootUser(app)
    transaction.commit()
    ZopeTestCase.close(app)


class SilvaLayer(ZopeLiteLayer):
    """Extend the ZopeLiteLayer to install a Silva instance.
    """

    @classmethod
    def setUp(cls):
        setDebugMode(1)
        import Products.Five.zcml as zcml
        zcml.load_site()
        setDebugMode(0)

        setupSilva()
        provideHandler(zope.component.eventtesting.events.append, (None,))

    @classmethod
    def tearDown(cls):
        cleanUp()


def setUp(test):
    """Setup before each tests.
    """
    app = ZopeTestCase.app()
    app.temp_folder.session_data._reset()
    zope.component.eventtesting.clearEvents()
    ZopeTestCase.close(app)

def tearDown(test):
    """Tear down after each tests.
    """
    noSecurityManager()



