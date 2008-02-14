from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

class ManagerServicesResourcesTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                       MixinRoleContent, MixinNavigate,
                                       MixinFieldParameters):
    """
    """

    def afterSetup(self):
        self.setUpMixin()

    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

    def test_manager_services(self):
        base_url = self.smi_url()
        base = None
        browser = Browser()
        # login
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        # build zmi url
        zmi_url = base_url.split('/')
        zmi_url.remove('root')
        zmi_url.remove('edit')
        zmi_url.append('manage_main')
        zmi_url = '/'.join(zmi_url)
        # goto zmi/manage_main
        browser.open(zmi_url)
        self.failUnless('Control_Panel (Control Panel)' in browser.contents)
        # click Silva root
        link = browser.getLink(url='root/manage_workspace')
        link.click()
        self.failUnless('Silva /edit...' in browser.contents)
        # click services tab
        link = browser.getLink('Services')
        link.click()
        self.failUnless('service_extensions (Silva Product and Extension Configuration)' in browser.contents)
        # click service_extensions
        link = browser.getLink('service_extensions (Silva Product and Extension Configuration)')
        link.click()
        self.failUnless('Configure Silva Extension Products' in browser.contents)
        # uninstall Silva Documents
        form = browser.getForm(index=3)
        form.getControl(name='uninstall:method').click()
        form = browser.getForm(index=3)
        self.failUnless('SilvaDocument uninstalled' in browser.contents)
        # install Silva Documents
        form.getControl(name='install:method').click()
        input = browser.getForm(index=3).getControl(name='uninstall:method').value
        self.failUnless('SilvaDocument installed' in browser.contents)
        # install Silva External Sources
        form = browser.getForm(index=2)
        form.getControl(name='install:method').click()
        self.failUnless('SilvaExternalSources installed' in browser.contents)
        # uninstall Silva External Sources
        form = browser.getForm(index=2)
        form.getControl(name='uninstall:method').click()
        self.failUnless('SilvaExternalSources uninstalled' in browser.contents)
        # refresh Silva Core
        form = browser.getForm(index=1)
        form.getControl(name='refresh:method').click()
        self.failUnless('Silva refreshed' in browser.contents)
        # install default layout
        form = browser.getForm(index=1)
        form.getControl(name='install_layout:method').click()
        self.failUnless('Default layout code installed' in browser.contents)
        # get back to the smi
        link = browser.getLink(url='root/manage_workspace')
        link.click()
        self.failUnless('Silva Root' in browser.contents)
        # click into the Silva instance
        link = browser.getLink(url='edit')
        link.click()
        self.failUnless('&#xab;root&#xbb;' in browser.contents)
        # logout
        self.do_logout(browser)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerServicesResourcesTestCase))
    return suite
