from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser
from urllib2 import HTTPError


class ManagerAssignRoleTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                MixinRoleContent, MixinNavigate,
                                MixinFieldParameters):
    """
        make dummy user
        login as manager
        navigate to access tab
        add dummy user and role
        logout as manager
        login as dummy user
        try to access none accessible content_type
        logout
    """

    def afterSetUp(self):
        self.setUpMixin()

    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

    def dummy_user(self):
        dummy_name = SilvaTestCase.user_dummy
        return dummy_name

    def test_manager_assign_role(self):
        # make the dummy user
        dummy_user = self.dummy_user()
        base_url = self.smi_url()
        base = None
        browser = Browser()
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        # click on the access tab
        tab_name = 'tab_access'
        test_condition = 'user roles for'
        browser.open(base_url)
        url = self.click_tab_name(browser, base_url, test_condition, tab_name)
        # logout
        self.do_logout(browser)
        
        # XXX
        # there is a redirect done in python, this makes the test hang until
        # you ctrl + c out. not sure how to work around this.
        # click on lookup users...
        #tab_name = 'lookup'
        #test_condition = 'user lookup at'
        #url = self.click_tab_name(browser, url, test_condition, tab_name)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerAssignRoleTestCase))
    return suite
