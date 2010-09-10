# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from SilvaBrowser import SilvaBrowser

from Products.Silva.testing import FunctionalLayer


def smi_settings(browser):
    browser.inspect.add(
        'feedback', '//div[@id="feedback"]/div/span')
    browser.links.add(
        'tabs', '//div[@class="tabs"]/a[contains(@class, "tab")]')
    browser.links.add(
        'subtabs', '//div[@class="middleground"]/div[@class="transporter"]/a')


class LocalSiteTestCase(unittest.TestCase):
    """Test if the local site screen, available in the properties tab
    of a Publication works.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        factory.manage_addFolder('folder', 'Folder')

    def test_localsite_simple(self):
        """We just activate/deactivate as a local site a publication.
        """
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/publication/edit'), 200)
        self.assertEqual(browser.links.tabs['properties'].click(), 200)

        self.assertTrue('local site...' in browser.links.subtabs.keys())
        self.assertEqual(browser.links.subtabs['local site'].click(), 200)

        self.assertEqual(
            browser.location,
            '/root/publication/edit/tab_localsite')

        form = browser.get_form('form')
        self.assertEqual(form.controls['form.action.make_site'].click(), 200)
        self.assertEqual(browser.inspect.feedback, ['Local site activated.'])

        form = browser.get_form('form')
        self.assertEqual(form.controls['form.action.delete_site'].click(), 200)
        # TODO: check new tab Services in ZMI
        self.assertEqual(browser.inspect.feedback, ['Local site deactivated.'])

    def test_localsite_still_in_use(self):
        """We test to disable a local site but it's in use.
        """
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/publication/edit'), 200)
        self.assertEqual(browser.links.tabs['properties'].click(), 200)
        self.assertEqual(browser.links.subtabs['local site'].click(), 200)

        form = browser.get_form('form')
        self.assertEqual(form.controls['form.action.make_site'].click(), 200)
        self.assertEqual(browser.inspect.feedback, ['Local site activated.'])

        factory = self.root.publication.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationService('service_customization')

        form = browser.get_form('form')
        self.assertEqual(form.controls['form.action.delete_site'].click(), 200)
        self.assertEqual(
            browser.inspect.feedback,
            ['Still have registered utilities.'])

        self.root.publication.manage_delObjects(['service_customization',])

        form = browser.get_form('form')
        self.assertEqual(form.controls['form.action.delete_site'].click(), 200)
        self.assertEqual(browser.inspect.feedback, ['Local site deactivated.'])

    def test_localsite_no_publication(self):
        """We should not have a local site ... buttons for Silva Root
        and Silva Forum, the configuration form should render
        correctly, if a user decide to access it.
        """
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager', 'manager')

        self.assertEqual(browser.open('/root/folder/edit'), 200)
        self.assertEqual(browser.links.tabs['properties'].click(), 200)

        self.assertTrue('local site...' not in browser.links.subtabs.keys())
        self.assertEqual(browser.open('/root/folder/edit/tab_localsite'), 404)

        self.assertEqual(browser.open('/root/edit'), 200)
        self.assertEqual(browser.links.tabs['properties'].click(), 200)

        self.assertTrue('local site...' not in browser.links.subtabs.keys())

    def test_localsite_others_user(self):
        """Others users than manager should not access that feature.
        """
        for user in ['chiefeditor', 'editor', 'author']:
            browser = self.layer.get_browser(smi_settings)
            browser.login(user, user)

            self.assertEqual(browser.open('/root/publication/edit'), 200)
            self.assertEqual(browser.links.tabs['properties'].click(), 200)

            self.assertTrue('local site...' not in browser.links.subtabs.keys())
            self.assertEqual(
                browser.open('/root/publication/edit/tab_localsite'),
                401)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LocalSiteTestCase))
    return suite
