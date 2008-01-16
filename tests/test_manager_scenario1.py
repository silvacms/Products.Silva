from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

class ManagerScenarioOneTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                 MixinRoleContent, MixinNavigate,
                                 MixinFieldParameters):
    """
        login manager
        select silva document
        make silva document
        enter silva document
        test tabs and buttons
    """
    
    def url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

    def test_manager_scenario_one(self):
        url = self.url()
        base = None
        browser = Browser()
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        self.do_create_content(browser, 'Silva Document',
                   self.fill_create_title_field, success)
        self.navigate_link(browser, url)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerScenarioOneTestCase))
    return suite
