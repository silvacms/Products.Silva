from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

class AuthorManagerScenarioOneTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                       MixinRoleContent, MixinNavigate,
                                       MixinFieldParameters):
    """
        login author
        select silva document
        make silva document
        enter silva document
        click preview
        logout
        login manager
        enter silva document
        click preview
        click publish
    """

    def afterSetUp(self):
        self.setUpMixin()

    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

    def test_author_manager_scenario_one(self):
        base_url = self.smi_url()
        base = None
        browser = Browser()
        # login author
        self.role_login_edit(browser, SilvaTestCase.user_author, success,
                             base=base)
        # create silva document
        self.do_create_content(browser, 'Silva Document',
                               self.fill_create_title_field, success)
        # click into the Document
        content = 'test_content'
        tab_name = 'tab_edit'
        link_text = 'test_content'
        test_condition = 'kupu editor'
        browser.open(base_url)
        url = self.click_content_link(browser, base_url, test_condition, content,
                                      link_text, tab_name)
        # click on the preview tab
        tab_name = 'tab_preview'
        link_text = 'preview'
        test_condition = 'public&nbsp;preview...'
        url = self.click_content_link(browser, url, test_condition, content,
                                      link_text, tab_name)
        # XXX
        # i'd go through the process of clicking on the publish tab and then
        # submit for approval, but it isn't possible to get the form from
        # browser.getForm(), because the form is nested in another.
        # this nesting can be found in tab_status.pt and tab_status_macros.pt
        # so instead i'm just going to log out, and the manager will take up
        # publishing the document.

        # click on the publish tab
        #tab_name = 'tab_status'
        #link_text = 'publish'
        #test_condition = 'status of'
        #url = self.click_content_link(browser, url, test_condition, content,
        #                              link_text, tab_name)
        # click on request approval
        #link_text = ''
        #test_condition = 'withdraw approval request'
        #url = self.click_content_link(browser, url, test_condition, content,
        #                              link_text, submit=True)
        # logout author
        self.do_logout(browser)
        # login manager
        browser = Browser()
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        # click into silva document
        content = 'test_content'
        tab_name = 'tab_edit'
        link_text = 'test_content'
        test_condition = 'kupu editor'
        browser.open(base_url)
        url = self.click_content_link(browser, base_url, test_condition, content,
                                      link_text, tab_name)
        # click prevew tab
        tab_name = 'tab_preview'
        link_text = 'preview'
        test_condition = 'public&nbsp;preview...'
        url = self.click_content_link(browser, base_url, test_condition, content,
                                      link_text, tab_name)
        # click the publish tab
        tab_name = 'tab_preview_publish'
        link_text = '\n        publish&nbsp;now\n      '
        test_condition = 'Version approved.'
        url = self.click_content_link(browser, url, test_condition, content,
                                      link_text, tab_name)
        # view the public document
        link_text = 'view public version'
        test_condition = '<h2 class="heading">test content</h2>'
        url = self.click_content_link(browser, url, test_condition, content,
                                    link_text)
        browser.goBack()
        self.do_logout(browser)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorManagerScenarioOneTestCase))
    return suite
