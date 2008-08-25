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


def setDebugMode(mode):
    """Allows manual setting of Five's inspection of debug mode to
    allow for zcml to fail meaningfully.
    """
    import Products.Five.fiveconfigure as fc
    fc.debug_mode = mode

def cleanUp():
    """Clean up component architecture"""
    _cleanUp()
    import Products.Five.zcml as zcml
    zcml._initialized = 0


def setupSilvaRoot(app, id='root', quiet=0):
    '''Creates a Silva root.'''
    if not hasattr(aq_base(app), id):
        _start = time.time()
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

def setupSilva(id='root', quiet=0):
    # Create a Silva site in the test (demo-) storage
    app = ZopeTestCase.app()
    setupSilvaRoot(app, id='root')
    transaction.commit()
    ZopeTestCase.close(app)


class SilvaZCMLLayer(ZopeLiteLayer):

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

