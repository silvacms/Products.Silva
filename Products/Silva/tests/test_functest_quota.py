# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.tests.helpers import test_filename
from Products.Silva.testing import FunctionalLayer, smi_settings


def smi_set_quota(browser, quota, should_fail=False):
    """Set the quota value, and expect a reply or an error.
    """

    form = browser.get_form('form')
    form.get_control('silva-quota.quota:record').value = quota
    assert form.get_control('save_metadata:method').click() == 200
    if should_fail:
        assert browser.inspect.form_error == [
            "The quota can't be negative or bigger than " \
                "the quota of the parent container."]
    else:
        assert browser.inspect.form_error == []
        assert browser.inspect.feedback == ['Metadata saved.']


def quota_settings(browser):
    smi_settings(browser)
    browser.inspect.add(
        'used_space',
        xpath='//div[@data-field-prefix="form.quotaform.field.size"]/div[@class="form-field"]')
    browser.inspect.add(
        'quota_space',
        xpath='//div[@data-field-prefix="form.quotaform.field.quota"]/div[@class="form-field"]')
    browser.macros.add('set_quota', smi_set_quota)


class EnableQuotaFunctionalTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_enable_quota(self):
        """Go in ZMI, and on service_extension enable the quota system.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager')
        browser.open('/root/manage_main')

        self.assertTrue('service' in browser.inspect.zmi_tabs)
        browser.inspect.zmi_tabs['service'].click()
        self.assertEqual(browser.location, '/root/manage_services')
        browser.inspect.zmi_listing['service_extensions'].click()
        self.assertEqual(
            browser.inspect.zmi_title,
            ['Extensions management'])

        form = browser.get_form('general')
        form.get_control('enable_quota_subsystem').click()
        self.assertEqual(
            browser.inspect.zmi_feedback,
            ['Quota sub-system enabled'])

class QuotaFunctionalTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        # Enable the quota system
        self.root.service_extensions.enable_quota_subsystem()
        factory = self.root.manage_addProduct['Silva']
        # Create test content
        factory.manage_addPublication('publication', 'Publication')

    def test_disable_quota(self):
        """Disable the quota system.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager')
        browser.open('/root/manage_main')

        self.assertTrue('service' in browser.inspect.zmi_tabs)
        browser.inspect.zmi_tabs['service'].click()
        browser.inspect.zmi_listing['service_extensions'].click()
        self.assertEqual(
            browser.inspect.zmi_title,
            ['Extensions management'])

        form = browser.get_form('general')
        form.get_control('disable_quota_subsystem').click()
        self.assertEqual(
            browser.inspect.zmi_feedback,
            ['Quota sub-system disabled'])

    def test_add_asset_overquota(self):
        """Test adding an asset (file and image) being overquota.
        """
        browser = self.layer.get_web_browser(quota_settings)
        browser.login('manager')
        browser.open('/root/edit')

        # Set quota to 1MB
        browser.macros.set_quota(1)
        self.assertEqual(browser.inspect.used_space, ['0'])
        self.assertEqual(
            browser.inspect.quota_space,
            ['(The quota for this area is set to 1 MB.)'])

        # Add a file and check the used space changed
        self.assertEqual(browser.inspect.tabs['contents'].click(), 200)

        form = browser.get_form('md.container')
        form.controls['md.container.field.content'].value = 'Silva File'
        self.assertEqual(form.controls['md.container.action.new'].click(), 200)

        odt_filename = test_filename('docs_export_2008-06-11.odt')
        form = browser.get_form('addform')
        form.get_control('addform.field.file').value = odt_filename
        self.assertEqual(form.get_control('addform.action.save').click(), 200)

        # Add you have an error.
        self.assertEqual(
            browser.html.xpath(
                'normalize-space(//body/div[contains(@class,"simple-page")]/h1/text())'),
            "Over Quota")
        self.assertEqual(
            browser.html.xpath(
                'normalize-space(//body/div[contains(@class,"simple-page")]/p[1]/text())'),
            "A quota is applied on the container you are working on, "
            "and the current operation would require 387.1 k more space.")

        self.assertEqual(
            browser.get_link('click here to continue').click(),
            200)
        self.assertEqual(browser.location, '/root/edit')
        self.assertFalse('odt' in browser.inspect.folder_listing)

    def test_add_asset(self):
        """Test adding an asset while the quota is on.
        """
        browser = self.layer.get_web_browser(quota_settings)
        browser.login('manager')

        self.assertEqual(browser.open('/root/edit'), 200)

        # Set quota to 10MB
        browser.macros.set_quota(10)
        self.assertEqual(browser.inspect.used_space, ['0'])
        self.assertEqual(
            browser.inspect.quota_space,
            ['(The quota for this area is set to 10 MB.)'])

        # Add a file and check the used space changed
        self.assertEqual(browser.inspect.tabs['contents'].click(), 200)
        browser.macros.create(
            'Silva File', id='odt', title='ODT Document',
            file=test_filename('docs_export_2008-06-11.odt'))
        self.assertEqual(browser.inspect.folder_listing['odt'].click(), 200)
        self.assertEqual(browser.location, '/root/odt/edit/tab_edit')

        self.assertEqual(browser.inspect.tabs['properties'].click(), 200)
        self.assertEqual(browser.inspect.subtabs['settings'].click(), 200)
        self.assertEqual(browser.location, '/root/odt/edit/tab_settings')
        self.assertEqual(browser.inspect.used_space, ['1.4 MB'])
        self.assertEqual(
            browser.inspect.quota_space,
            ['(The quota for this area is set to 10 MB.)'])

        self.assertEqual(browser.inspect.navigation['root'].click(), 200)
        self.assertEqual(browser.location, '/root/edit/tab_settings')
        self.assertEqual(browser.inspect.used_space, ['1.4 MB'])
        self.assertEqual(
            browser.inspect.quota_space,
            ['(The quota for this area is set to 10 MB.)'])

    def test_set_quota(self):
        """Test modification of the quota's value.
        """
        browser = self.layer.get_web_browser(quota_settings)
        browser.login('manager')

        browser.open('/root/edit')

        self.assertTrue('settings' in browser.inspect.content_tabs)
        browser.inspect.content_tabs['settings'].click()
        self.assertTrue('settings' in browser.inspect.content_subtabs)
        browser.inspect.content_subtabs['settings'].click()

        self.assertEqual(browser.inspect.used_space, ['0'])
        self.assertEqual(browser.inspect.quota_space, [])

        # check and set quota
        browser.macros.set_quota(10)
        self.assertEqual(
            browser.inspect.quota_space,
            ['(The quota for this area is set to 10 MB.)'])

        # go to the publication
        browser.inspect.content_tabs['contents'].click()
        self.assertEqual(browser.inspect.folder_identifier, ['publication'])
        browser.inspect.folder_goto[0].click()

        self.assertTrue('settings' in browser.inspect.content_tabs)
        browser.inspect.content_tabs['settings'].click()
        self.assertTrue('settings' in browser.inspect.content_subtabs)
        browser.inspect.content_subtabs['settings'].click()

        self.assertEqual(browser.inspect.used_space, ['0'])
        self.assertEqual(
            browser.inspect.quota_space,
            ['(The quota for this area is set to 10 MB.)'])

        # put a correct quota, which is smaller than the parent one, 10MB.
        browser.macros.set_quota(5)
        self.assertEqual(
            browser.inspect.quota_space,
            ['(The quota for this area is set to 5 MB.)'])

        # put a quota to 0, the value of the parent one is expected.
        browser.macros.set_quota(0)
        self.assertEqual(
            browser.inspect.quota_space,
            ['(The quota for this area is set to 10 MB.)'])
        browser.macros.set_quota('')
        self.assertEqual(
            browser.inspect.quota_space,
            ['(The quota for this area is set to 10 MB.)'])

        # put a quota of 100Mb which is bigger than the one of the parent
        browser.macros.set_quota(100, should_fail=True)
        self.assertEqual(
            browser.inspect.quota_space,
            ['(The quota for this area is set to 10 MB.)'])

        # put a quota which is negative
        browser.macros.set_quota(-3, should_fail=True)
        self.assertEqual(
            browser.inspect.quota_space,
            ['(The quota for this area is set to 10 MB.)'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EnableQuotaFunctionalTestCase))
    suite.addTest(unittest.makeSuite(QuotaFunctionalTestCase))
    return suite
