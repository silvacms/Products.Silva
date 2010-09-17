# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl.SecurityManagement import newSecurityManager
import Products.Silva
from Products.Silva.ftesting import smi_settings

from infrae.testbrowser.browser import Browser as NewBrowser
from infrae.testing import TestCase, suite_from_package
from infrae.testing import get_event_names, clear_events, get_events
from infrae.testing import assertNotTriggersEvents, assertTriggersEvents
from infrae.wsgi.testing import BrowserLayer, Browser, http
from zope.site.hooks import setSite, setHooks
import transaction


class SilvaLayer(BrowserLayer):
    """Test layer inside Silva.
    """
    default_products = BrowserLayer.default_products + [
        'BTreeFolder2',
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
        'MailHost',
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
    default_users = {
        'editor': ['Editor'],
        'manager': ['Manager'],
        'chiefeditor': ['ChiefEditor'],
        'author': ['Author'],
        'reader': ['Reader'],
        'viewer': ['Viewer'],
        'dummy': [],}

    def _install_application(self, app):
        """Install Silva in the test application.
        """
        # Add a user
        userfolder = app.acl_users
        user = userfolder.getUserById('manager').__of__(userfolder)

        # Loging to that user and add a Silva Root
        newSecurityManager(None, user)
        app.manage_addProduct['Silva'].manage_addRoot('root', '')

        # Commit changes
        transaction.commit()

    def testSetUp(self):
        super(SilvaLayer, self).testSetUp()

        # Get the Silva Root and set it as a local site
        app = super(SilvaLayer, self).get_application()
        self._silva_root = app.root
        setSite(self._silva_root)
        setHooks()

    def testTearDown(self):
        # Reset local site to None
        setSite(None)
        setHooks()
        self._silva_root = None

        super(SilvaLayer, self).testTearDown()

    def get_application(self):
        """Return the application, here the Silva Root.
        """
        return self._silva_root

    def get_browser(self, settings=None):
        browser = NewBrowser(self._test_wsgi_application)
        if settings is not None:
            settings(browser)
        return browser


FunctionalLayer = SilvaLayer(Products.Silva)


__all__ = ['FunctionalLayer', 'SilvaLayer',
           'TestCase', 'suite_from_package',
           'Browser', 'http',
           'get_event_names', 'clear_events', 'get_events',
           'assertNotTriggersEvents', 'assertTriggersEvents',]
