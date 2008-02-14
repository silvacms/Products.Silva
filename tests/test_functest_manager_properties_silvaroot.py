from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

class ManagerPropertiesSilvaRootTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                         MixinRoleContent, MixinNavigate,
                                         MixinFieldParameters):
    """
        test properties tabs 'settings...' and 'addables...' as manager
    """

    def afterSetUp(self):
        self.setUpMixin()

    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

    def test_manager_properties_silvaroot(self):
        base_url = self.smi_url()
        base = None
        browser = Browser()
        # login
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        # click on the properties button
        tab_name = 'tab_metadata'
        test_condition = 'metadata set'
        self.click_tab_name(browser, base_url, test_condition, tab_name)
        # click on the addables button
        tab_name = 'tab_addables'
        test_condition = 'If checked, inherit the addables from above'
        self.click_tab_name(browser, base_url, test_condition, tab_name)
        # logout
        self.do_logout(browser)
        # uncheck the checked boxes
        # XXX
        # seems the only way i can use selected is by a label name, however the
        # fields on this page have been built in formulator which doesn't make
        # label tags. been trying to use selected by a checkbox name, but that
        # doesn't work!?!
        #browser.getControl(name='field_acquire_addables').selected = False
        #browser.getControl(name='form_submitted').click()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerPropertiesSilvaRootTestCase))
    return suite
