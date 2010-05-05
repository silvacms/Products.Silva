# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

from silva.wsgi.testing import BrowserLayer
from zope.site.hooks import setSite, setHooks
import transaction


class SilvaLayer(BrowserLayer):
    """Test layer inside Silva.
    """
    default_products = BrowserLayer.default_products + [
        'ZCatalog',
        'TemporaryFolder',
        'ZCTextIndex',
        'PythonScripts',
        'PageTemplates',
        'Formulator',
        'FileSystemSite',
        'ParsedXML',
        'ProxyIndex',
        'MaildropHost',
        'ExtFile',
        'Groups',
        'SilvaFind',
        'SilvaMetadata',
        'SilvaViews',
        'SilvaExternalSources',
        'SilvaDocument',
        'Silva',
        ]
    default_packages = BrowserLayer.default_packages + [
        'silva.core.references',
        'silva.core.views',
        'silva.core.layout',
        'silvatheme.standardissue',
        'silva.core.services',
        ]

    def _install_app(self, app):
        """Install Silva in the test application.
        """
        # Add a user
        uf = app.acl_users
        uf._doAddUser('silvatestcase', '', ['Manager'], [])
        user = uf.getUserById('silvatestcase').__of__(uf)

        # Loging to that user and add a Silva Root
        newSecurityManager(None, user)
        app.manage_addProduct['Silva'].manage_addRoot('root', '')

        # Commit changes
        transaction.commit()

    def get_application(self):
        """Return the application, here the Silva Root.
        """
        app = super(SilvaLayer, self).get_application()
        root = app.root
        setSite(root)
        setHooks()
        return root

