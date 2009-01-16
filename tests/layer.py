# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import time

# Zope 3
import zope.component.eventtesting
from zope.component import provideHandler
from zope.testing.cleanup import cleanUp as _cleanUp

# Zope 2
from ZODB.DemoStorage import DemoStorage
from Testing import ZopeTestCase
from Testing.ZopeTestCase import installProduct, hasProduct
from Testing.ZopeTestCase.layer import ZopeLiteLayer
from Testing.ZopeTestCase.layer import onsetup as ZopeLiteLayerSetup
from AccessControl.SecurityManagement import newSecurityManager, \
    noSecurityManager
import transaction


@ZopeLiteLayerSetup
def installPackage(name):
    """We need to overrides that because a nice Plone developer
    funk-up ZopeLite.
    """
    ZopeTestCase.installPackage(name)

# Install Zope 2 Products

installProduct('ZCatalog')
installProduct('TemporaryFolder')
installProduct('ZCTextIndex')
installProduct('PythonScripts')
installProduct('PageTemplates')
installProduct('Formulator')
installProduct('FileSystemSite')
installProduct('ParsedXML')
installProduct('XMLWidgets')
installProduct('ProxyIndex')
if hasProduct('MaildropHost'):
    installProduct('MaildropHost')
if hasProduct('ExtFile'):
    installProduct('ExtFile')
installProduct('Groups')
installProduct('SilvaFind')
installProduct('SilvaMetadata')
installProduct('SilvaViews')
if hasProduct('SilvaExternalSources'):
    installProduct('SilvaExternalSources')
installProduct('SilvaDocument')
installProduct('Silva')
installProduct('Five')
installPackage('silva.core.views')
installPackage('silva.core.layout')

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
    if not hasattr(app, 'root'):
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
        import silva.export.opendocument
        zcml.load_site()
        zcml.load_config('configure.zcml', silva.export.opendocument)
        setDebugMode(0)

        setupSilva()
        provideHandler(zope.component.eventtesting.events.append, (None,))

    @classmethod
    def tearDown(cls):
        cleanUp()


class SilvaFunctionalLayer(SilvaLayer):
    """Separate test from functional tests (for the moment).
    """


class SilvaGrokLayer(SilvaLayer):
    """Separate Grok test from regular Silva ones.
    """


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



