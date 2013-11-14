# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import re
import email
import os.path
import sys
import tempfile

from AccessControl.SecurityManagement import newSecurityManager
from OFS.SimpleItem import SimpleItem
from Products.Silva import MAILHOST_ID
from Products.Silva.EmailMessageService import email_queue
from Products.Silva.tests.mockers import install_mockers
from silva.core.services import CatalogingTask
import Products.Silva

from infrae.testbrowser.browser import Browser
from infrae.testbrowser.selenium.browser import Browser as SeleniumBrowser
from infrae.testing import TestCase, TestMethods, suite_from_package
from infrae.testing import get_event_names, clear_events, get_events
from infrae.testing import assertNotTriggersEvents, assertTriggersEvents
from infrae.testing import testCleanUp
from infrae.fileupload.middleware import UploadMiddleware
from infrae.wsgi.testing import BrowserLayer, TestRequest
from zope.site.hooks import setSite, setHooks
from fanstatic import Fanstatic
import transaction


SENT_MAILS = []


class Transaction(object):
    """Commit the code executed.
    """

    def __init__(self, catalog=False):
        self._catalog = catalog

    def __enter__(self):
        transaction.abort()
        transaction.begin()
        if self._catalog:
            CatalogingTask.get().activate()

    def __exit__(self, t, v, tb):
        if v is None and not transaction.isDoomed():
            transaction.commit()
        else:
            transaction.abort()


class CatalogTransaction(Transaction):
    """Commit the code executed, using a catalog queue
    """

    def __init__(self):
        super(CatalogTransaction, self).__init__(catalog=True)


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


testCleanUp.add(MockMailHost.reset)
testCleanUp.add(email_queue.clear)

class SilvaLayer(BrowserLayer):
    """Test layer inside Silva.
    """
    default_products = BrowserLayer.default_products + [
        'BTreeFolder2',
        'TemporaryFolder',
        'ZCatalog',
        'ZCTextIndex',
        'PythonScripts',
        'PageTemplates',
        'Formulator',
        'GenericSetup',
        'PluggableAuthService',
        'MaildropHost',
        'MailHost',
        'SilvaMetadata',
        'Silva',
        ]
    default_packages = BrowserLayer.default_packages + [
        'silva.core.references',
        'silva.core.views',
        'silva.core.layout',
        'silva.core.services',
        'silvatheme.standardissue',
        'silva.pas.base',
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
        if 'service_ui' in app.root.objectIds():
            app.root.service_ui.test_mode = True
            app.root.service_ui.folder_goto_menu = True

        install_mockers(app.root)

        # Commit changes
        transaction.commit()

    def testSetUp(self):
        super(SilvaLayer, self).testSetUp()

        # Get the Silva Root and set it as a local site
        app = super(SilvaLayer, self).get_application()
        self._silva_root = app.root
        setSite(self._silva_root)
        setHooks()

        # List of created browsers
        self._browsers = []

    def testTearDown(self):
        # Clean browsers
        for browser in self._browsers:
            try:
                browser.close()
            except:
                pass
        self._browsers = []
        self._silva_root = None

        super(SilvaLayer, self).testTearDown()

    def get_application(self):
        """Return the application, here the Silva Root.
        """
        return self._silva_root

    def get_wsgi_application(self):
        """Return a WSGI application, that can be used to query the
        Silva Root.
        """
        return UploadMiddleware(
            Fanstatic(
                self._test_wsgi_application,
                minified=True,
                bundle=True,
                publisher_signature='++static++'),
            tempfile.gettempdir())

    def get_browser(self, settings=None):
        """A lxml-based based-browser, that case be used for simple
        functional testing.
        """
        browser = Browser(self.get_wsgi_application())
        if settings is not None:
            settings(browser)
        self._browsers.append(browser)
        return browser

    def get_web_browser(self, settings=None):
        """Return a Selenium based-browser, that case be used for
        advanced (with JS) functional testing.
        """
        browser = SeleniumBrowser(self.get_wsgi_application())
        if settings is not None:
            settings(browser)
        self._browsers.append(browser)
        return browser

    def get_fixture(self, filename, globs=None):
        """Return the full path to the given fixure. If globs is not
        given, the base path will a directory tests/data defined
        relatively from the definition of the test layer.
        """
        if globs is None:
            module = sys.modules[self.__class__.__module__]
            base_path = os.path.join(os.path.dirname(module.__file__), 'tests')
        else:
            base_path = os.path.dirname(globs['__file__'])
        return os.path.join(base_path, 'data', filename)

    def open_fixture(self, filename, globs=None, mode='rb'):
        """Open the given test file. If globs is not given, it will
        look inside a directory located in tests/data relatively from
        the definition of the test layer.
        """
        return open(self.get_fixture(filename, globs), mode)


FunctionalLayer = SilvaLayer(Products.Silva)

tests = TestMethods()

__all__ = ['FunctionalLayer', 'SilvaLayer', 'tests',
           'TestCase', 'TestMethods', 'TestCase', 'TestRequest',
           'suite_from_package',
           'get_event_names', 'clear_events', 'get_events',
           'assertNotTriggersEvents', 'assertTriggersEvents',]
