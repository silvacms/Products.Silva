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
        form1.getControl(name='install_layout:method').click()
        self.failUnless('Default layout code installed' in sb.browser.contents)

        # uninstall SilvaDocument
        form2 = sb.browser.getForm(index=2)
        input_hidden = form2.getControl(name='name')
        self.assertEquals(input_hidden.value, 'SilvaDocument')
        form2.getControl(name='uninstall:method').click()
        self.failUnless('SilvaDocument uninstalled' in sb.browser.contents)
        
        # install Silva Documents
        form2 = sb.browser.getForm(index=2)
        input_hidden = form2.getControl(name='name')
        self.assertEquals(input_hidden.value, 'SilvaDocument')
        form2.getControl(name='install:method').click()
        self.failUnless('SilvaDocument installed' in sb.browser.contents)

        # uninstall SilvaFind
        form3 = sb.browser.getForm(index=3)
        input_hidden = form3.getControl(name='name')
        self.assertEquals(input_hidden.value, 'SilvaFind')
        form3.getControl(name='uninstall:method').click()
        self.failUnless('SilvaFind uninstalled' in sb.browser.contents)

        # install SilvaFind
        form3 = sb.browser.getForm(index=3)
        input_hidden = form3.getControl(name='name')
        self.assertEquals(input_hidden.value, 'SilvaFind')
        form3.getControl(name='install:method').click()
        self.failUnless('SilvaFind installed' in sb.browser.contents)

        # install SilvaExternalSources
        form4 = sb.browser.getForm(index=4)
        input_hidden = form4.getControl(name='name')
        self.assertEquals(input_hidden.value, 'SilvaExternalSources')
        form4.getControl(name='install:method').click()
        self.failUnless('SilvaExternalSources installed' in sb.browser.contents)

        # uninstall SilvaExternalSources
        form4 = sb.browser.getForm(index=4)
        input_hidden = form4.getControl(name='name')
        self.assertEquals(input_hidden.value, 'SilvaExternalSources')
        form4.getControl(name='uninstall:method').click()
        self.failUnless('SilvaExternalSources uninstalled' in sb.browser.contents)

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
