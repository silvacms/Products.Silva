# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class ManagerServicesResourcesTestCase(SilvaFunctionalTestCase):
    """
        test the service tab
        install/uninstall silva products
    """

    def test_manager_services(self):
        sb = SilvaBrowser()
        # login
        status, url = sb.login('manager', 'secret', sb.smi_url())
        # goto zmi/manage_main
        sb.go('http://nohost/manage_main')
        self.failUnless('Control_Panel (Control Panel)' in sb.browser.contents)
        # click Silva root
        sb.go('http://nohost/root/manage_workspace')
        self.failUnless('Silva /edit...' in sb.browser.contents)
        # click services tab
        sb.click_href_labeled('Services')
        self.failUnless('service_extensions (Silva Product and Extension Configuration)' in sb.browser.contents)
        # click service_extensions
        sb.click_href_labeled('service_extensions (Silva Product and Extension Configuration)')
        self.failUnless('Configure Silva Extension Products' in sb.browser.contents)

        # install Silva Core
        form1 = sb.browser.getForm(index=1)
        input_hidden = form1.getControl(name='name')
        self.assertEquals(input_hidden.value, 'Silva')
        form1.getControl(name='install_layout').click()
        self.failUnless('Default legacy layout code installed' in sb.browser.contents)

        # Test to uninstall/reinstall already installed extensions.
        for extension in ['SilvaDocument',  'SilvaFind']:
            # uninstall it
            form = sb.browser.getForm(name=extension)
            input_hidden = form.getControl(name='name')
            self.assertEquals(input_hidden.value, extension)
            form.getControl(name='uninstall').click()
            self.failUnless(('%s uninstalled' % extension) in sb.browser.contents)

            # install it
            form = sb.browser.getForm(name=extension)
            form.getControl(name='install').click()
            self.failUnless(('%s installed' % extension) in sb.browser.contents)


        # get back to the smi
        sb.go('http://nohost/root/manage_workspace')
        self.failUnless('Silva Root' in sb.browser.contents)
        # click into the Silva instance
        sb.click_href_labeled('Silva /edit...')
        self.failUnless('&#xab;root&#xbb;' in sb.browser.contents)
        # logout
        status, url = sb.click_href_labeled('logout')
        self.assertEquals(status, 401)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerServicesResourcesTestCase))
    return suite
