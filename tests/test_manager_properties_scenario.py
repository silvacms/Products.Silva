from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

class ManagerPropertiesScenarioTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                        MixinRoleContent, MixinNavigate,
                                        MixinFieldParameters):
    """
        login manager
        select silva document
        make silva document
        click properties tab
    """

    def afterSetUp(self):
        self.setUpMixin()

    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()

    def test_manager_properties(self):
        base_url = self.smi_url()
        base = None
        browser = Browser()
        # login
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        # create silva document
        self.do_create_content(browser, 'Silva Document',
                               self.fill_create_title_field, success)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerPropertiesScenarioTestCase))
    return suite
