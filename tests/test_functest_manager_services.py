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
        # uninstall Silva Documents
        form = sb.browser.getForm(index=3)
        form.getControl(name='uninstall:method').click()
        form = sb.browser.getForm(index=3)
        self.failUnless('SilvaDocument uninstalled' in sb.browser.contents)
        # install Silva Documents
        form.getControl(name='install:method').click()
        input = sb.browser.getForm(index=3).getControl(name='uninstall:method').value
        self.failUnless('SilvaDocument installed' in sb.browser.contents)
        # install Silva External Sources
        form = sb.browser.getForm(index=2)
        form.getControl(name='install:method').click()
        self.failUnless('SilvaExternalSources installed' in sb.browser.contents)
        # uninstall Silva External Sources
        form = sb.browser.getForm(index=2)
        form.getControl(name='uninstall:method').click()
        self.failUnless('SilvaExternalSources uninstalled' in sb.browser.contents)
        # refresh Silva Core
        form = sb.browser.getForm(index=1)
        form.getControl(name='refresh:method').click()
        self.failUnless('Silva refreshed' in sb.browser.contents)
        # install default layout
        form = sb.browser.getForm(index=1)
        form.getControl(name='install_layout:method').click()
        self.failUnless('Default layout code installed' in sb.browser.contents)
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
