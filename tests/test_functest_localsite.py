# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class LocalSiteTestCase(SilvaFunctionalTestCase):
    """Test if the local site screen, available in the properties tab
    of a Publication works.
    """

    def afterSetUp(self):
        self.add_publication(self.root, 'pub', 'Pub')
        self.add_folder(self.root, 'folder', 'Folder')

    def test_localsite_simple(self):
        """We just activate/deactivate as a local site a publication.
        """
        browser = SilvaBrowser()
        browser.login('manager', url='http://nohost/root/pub/edit')
        browser.click_tab_named('properties')
        self.assertEquals(
            list(browser.get_middleground_buttons()),
            [u'settings...', u'addables...',
             u'local site...', u'customization...'])
        browser.click_href_labeled('local site...')
        self.assertEquals(browser.get_url(),
                          'http://nohost/root/pub/edit/tab_localsite')
        browser.click_control_labeled("make local site")
        feedback = browser.get_status_feedback()
        self.failUnless(feedback.startswith('Local site activated.'))
        # TODO: check new tab Services in ZMI
        browser.click_control_labeled("remove local site")
        feedback = browser.get_status_feedback()
        self.failUnless(feedback.startswith('Local site deactivated.'))

    def test_localsite_still_in_use(self):
        """We test to disable a local site but it's in use.
        """
        browser = SilvaBrowser()
        browser.login('manager',
                      url='http://nohost/root/pub/edit/tab_localsite')
        browser.click_control_labeled("make local site")
        feedback = browser.get_status_feedback()
        self.failUnless(feedback.startswith('Local site activated.'))
        factory = self.root.pub.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationService('service_customization')
        browser.click_control_labeled("remove local site")
        self.assertEquals(browser.get_alert_feedback(),
                          'Still have registered utilities.')
        self.root.pub.manage_delObjects(['service_customization',])
        browser.click_control_labeled("remove local site")
        feedback = browser.get_status_feedback()
        self.failUnless(feedback.startswith('Local site deactivated.'))

    def test_localsite_no_publication(self):
        """We should not have a local site ... buttons for Silva Root
        and Silva Forum, the configuration form should render
        correctly, if a user decide to access it.
        """
        browser = SilvaBrowser()
        browser.login('manager', url='http://nohost/root/edit')
        browser.click_tab_named('properties')
        self.failIf(u'local site ...' in
                    list(browser.get_middleground_buttons()))
        code, url = browser.go('http://nohost/root/edit/tab_localsite')
        self.assertEquals(code, 200)
        browser.go('http://nohost/root/folder/edit')
        browser.click_tab_named('properties')
        self.failIf(u'local site ...' in
                    list(browser.get_middleground_buttons()))
        code, url = browser.go('http://nohost/root/folder/edit/tab_localsite')
        self.assertEquals(code, 404)

    def test_localsite_others_user(self):
        """Others users than manager should not access that feature.
        """
        for user in ['chiefeditor', 'editor', 'author']:
            browser = SilvaBrowser()
            browser.login(user, url='http://nohost/root/pub/edit')
            browser.click_href_labeled('pub')
            browser.click_tab_named('properties')
            self.failIf(u'local site ...' in
                        list(browser.get_middleground_buttons()))
            code, url = browser.go('http://nohost/root/pub/edit/tab_localsite')
            self.assertEquals(code, 401)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LocalSiteTestCase))
    return suite
