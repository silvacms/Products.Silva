from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

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

    def dummy_user(self):
        dummy_name = SilvaTestCase.dummy_name
        dummy_pass = SilvaTestCase.dummy_password

    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

    def test_manager_assign_role(self):
        # make the dummy user
        self.dummy_user()
        base_url = self.smi_url
        base = None
        browser = Browser()
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerAssignRoleTestCase))
    return suite
