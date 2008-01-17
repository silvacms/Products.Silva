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
    
    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

    def preview_url(self, content):
        url = '%s/%s' % (self.getRoot().absolute_url(), content)
        return url

    def test_manager_scenario_one(self):
        base_url = self.smi_url()
        base = None
        browser = Browser()
        # login
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        # create silva document
        self.do_create_content(browser, 'Silva Document',
                               self.fill_create_title_field, success)
        test_condition = 'kupu editor'
        content = 'test_content'
        tab_name = 'tab_edit'
        link = self.click_content_link(browser, base_url, test_condition, content,
                                       tab_name)
        test_condition = 'public&nbsp;preview...'
        tab_name = 'tab_preview'
        self.click_content_link(browser, link, test_condition, content,
                                tab_name)
        public_view_url = self.preview_url(content)
        test_condition = 'Sorry, this Silva Document is not viewable.'
        self.click_content_link(browser, public_view_url, test_condition, content)
        # click on preview_tab in kupu editor
        # /test_content/edit/tab_preview
        #self.content_preview_tab(base_url, test_condition, content)
        self.do_logout(browser)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerScenarioOneTestCase))
    return suite
