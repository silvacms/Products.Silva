# fCopyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import re
import email

from AccessControl.SecurityManagement import newSecurityManager
from OFS.SimpleItem import SimpleItem
from Products.Silva import MAILHOST_ID
from Products.Silva.ftesting import smi_settings
import Products.Silva

from infrae.testbrowser.browser import Browser as NewBrowser
from infrae.testing import TestCase, suite_from_package
from infrae.testing import get_event_names, clear_events, get_events
from infrae.testing import assertNotTriggersEvents, assertTriggersEvents
from infrae.wsgi.testing import BrowserLayer, Browser, http
from zope.site.hooks import setSite, setHooks
import transaction


SENT_MAILS = []


class MockMail(object):
    """A sent mail. We can access data about this email for testing
    purpose as well.
    """

    def __init__(self, mfrom, mto, message):
        self.mfrom = mfrom
        self.mto = mto
        self.message = message
        self.__parsed = email.parser.Parser().parsestr(message)

    @property
    def subject(self):
        return self.__parsed.get('Subject')

    @property
    def headers(self):
        return dict(self.__parsed)

    @property
    def content_type(self):
        return self.__parsed.get_content_type()

    @property
    def charset(self):
        return self.__parsed.get_content_charset()

    @property
    def text(self):
        return self.__parsed.get_payload()

    @property
    def urls(self):
        URLS = re.compile(r'(mailto\:|news|(ht|f)tp(s?)\://){1}\S+')
        return [m.group() for m in re.finditer(URLS, self.text)]

    def __repr__(self):
        return '<Message from %s to %s>' % (self.mfrom, ', '.join(self.mto))


class MockMailHost(SimpleItem):
    """A fake mail host that retains its email for testing purpose.
    """
    meta_type = 'Mock Mail Host'

    def __init__(self, id):
        super(MockMailHost, self).__init__(id)
        self.reset()

    @property
    def messages(self):
        return list(SENT_MAILS)

    @staticmethod
    def reset():
        del SENT_MAILS[:]

    def read_last_message(self):
        message = None
        if SENT_MAILS:
            message = SENT_MAILS[-1]
        self.reset()
        return message

    def _send(self, mfrom, mto, message):
        SENT_MAILS.append(MockMail(mfrom=mfrom, mto=mto, message=message))


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
        'FileSystemSite',
        'Formulator',
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
        'silva.core.services'
        'silva.core.contentlayout',
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

        if MAILHOST_ID in app.root.objectIds():
            app.root.manage_delObjects([MAILHOST_ID])
            app.root._setObject(MAILHOST_ID, MockMailHost(MAILHOST_ID))

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
        MockMailHost.reset()

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
           'Browser', 'http', 'smi_settings',
           'get_event_names', 'clear_events', 'get_events',
           'assertNotTriggersEvents', 'assertTriggersEvents',]
