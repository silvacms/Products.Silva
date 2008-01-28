from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

class ManagerPropertiesSilvaRootTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                         MixinRoleContent, MixinNavigate,
                                         MixinFieldParameters):
    """
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
        link_text = 'addables...'
        test_condition = 'addables...'

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerPropertiesSilvaRootTestCase))
    return suite
