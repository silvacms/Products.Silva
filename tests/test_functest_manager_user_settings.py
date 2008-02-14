from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

class ManagerUserSettingsTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                       MixinRoleContent, MixinNavigate,
                                       MixinFieldParameters):
    """
    """

    def afterSetup(self):
        self.setUpMixin()

    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

    def test_manager_user_settings(self):
        base_url = self.smi_url()
        base = None
        browser = Browser()
        # login
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        browser.open(base_url)
        link = browser.getLink('user settings')
        link.click()
        form = browser.getForm(name='user_settings_form')
        form.getControl(name='field_fullname').value = 'test_bill'
        form.getControl(name='field_email').value = 'test@example.com'
        form.getControl(name='langsetting').value = ['it']
        form.getControl(name='field_editor').value = ['forms editor']
        form.getControl(name='save_memberdata:method').click()
        self.assertEquals(browser.getControl(name='field_fullname').value, 'test_bill')
        self.assertEquals(browser.getControl(name='field_email').value, 'test@example.com')
        f = browser.getControl('italiano').selected
        self.assertEquals(f, True)
        f = browser.getControl('forms editor').selected
        self.assertEquals(f, True)
        form = browser.getForm(name='user_settings_form')
        # XXX js onclick to close!!!
        # so i just logout
        # logout
        self.do_logout(browser)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerUserSettingsTestCase))
    return suite
