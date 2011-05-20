# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import transaction
from Products.Silva.testing import FunctionalLayer, smi_settings


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
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login('manager')

        browser.open('/root/publication/edit')
        self.assertTrue('settings' in browser.inspect.content_tabs)

        browser.inspect.content_tabs['settings'].click()
        self.assertTrue('local site' in browser.inspect.content_subtabs)

        browser.inspect.content_subtabs['local site'].click()

        # Local site form.
        self.assertEqual(browser.inspect.form_controls, ['Make local site'])
        browser.inspect.form_controls['make'].click()
        self.assertEqual(browser.inspect.feedback, ['Local site activated.'])

        # You now have a services tab in ZMI
        browser.open('/root/publication/manage_main')
        self.assertTrue('services' in browser.inspect.zmi_tabs)
        browser.inspect.zmi_tabs['services'].click()
        browser.inspect.zmi_tabs['edit'].click()

        self.assertTrue('settings' in browser.inspect.content_tabs)
        browser.inspect.content_tabs['settings'].click()
        self.assertTrue('local site' in browser.inspect.content_subtabs)
        browser.inspect.content_subtabs['local site'].click()

        # Local site form.
        self.assertEqual(browser.inspect.form_controls, ['Remove local site'])
        browser.inspect.form_controls['remove'].click()
        self.assertEqual(browser.inspect.feedback, ['Local site deactivated.'])

        # The service tab is gone
        browser.open('/root/publication/manage_main')
        self.assertFalse('services' in browser.inspect.zmi_tabs)

    def test_localsite_still_in_use(self):
        """We test to disable a local site but it's in use.
        """
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login('manager')

        browser.open('/root/publication/edit')

        self.assertTrue('settings' in browser.inspect.content_tabs)
        browser.inspect.content_tabs['settings'].click()
        self.assertTrue('local site' in browser.inspect.content_subtabs)
        browser.inspect.content_subtabs['local site'].click()

        # Enable the site
        self.assertEqual(browser.inspect.form_controls, ['Make local site'])
        browser.inspect.form_controls['make'].click()
        self.assertEqual(browser.inspect.feedback, ['Local site activated.'])

        # Add a local service.
        factory = self.root.publication.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationService('service_customization')
        transaction.commit()

        browser.inspect.content_tabs['content'].click()
        browser.inspect.content_tabs['settings'].click()
        browser.inspect.content_subtabs['local site'].click()

        # We try to remove the site, but have a service still.
        self.assertEqual(browser.inspect.form_controls, ['Remove local site'])
        browser.inspect.form_controls['remove'].click()
        self.assertEqual(
            browser.inspect.feedback,
            ['Still have registered services.'])

        self.root.publication.manage_delObjects(['service_customization',])
        transaction.commit()

        browser.inspect.content_tabs['content'].click()
        browser.inspect.content_tabs['settings'].click()
        browser.inspect.content_subtabs['local site'].click()

        # We try to remove the site, we have no service, it should work.
        self.assertEqual(browser.inspect.form_controls, ['Remove local site'])
        browser.inspect.form_controls['remove'].click()
        self.assertEqual(browser.inspect.feedback, ['Local site deactivated.'])

    def test_localsite_no_publication(self):
        """We should not have a local site ... buttons for Silva Root
        and Silva Forum, the configuration form should render
        correctly, if a user decide to access it.
        """
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login('manager')

        browser.open('/root/folder/edit')
        self.assertTrue('settings' in browser.inspect.content_tabs)

        browser.inspect.content_tabs['settings'].click()
        self.assertFalse('local site' in browser.inspect.content_subtabs)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LocalSiteTestCase))
    return suite
