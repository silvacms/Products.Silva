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
        click preview tab
        click public view
        click back
        click publish now tab
        click public view
        click back
        logout
    """

    def afterSetUp(self):
        self.setUpMixin()
    
    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
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
        # click into the Silva Document
        # set parameters for operation
        content = 'test_content'
        tab_name = 'tab_edit'
        link_text = 'test_content'
        test_condition = 'kupu editor'
        # build the link
        browser.open(base_url)
        url = self.click_content_link(browser, base_url, test_condition, content,
                                      link_text, tab_name)
        # click on the preview tab
        tab_name = 'tab_preview'
        link_text = 'preview'
        test_condition = 'public&nbsp;preview...'
        url = self.click_content_link(browser, url, test_condition, content,
                                      link_text, tab_name)
        # click the public view link
        link_text = 'view public version'
        test_condition = 'Sorry, this Silva Document is not viewable.'
        url = self.click_content_link(browser, url, test_condition, content,
                                      link_text)
        # oops, document not viewable, go back to public preview
        browser.goBack()
        url = browser.url
        self.failUnless('public&nbsp;preview' in browser.contents)
        self.failUnless('<h2 class="heading">test content</h2>' in browser.contents)
        # click publish now button
        tab_name = 'tab_preview_publish'
        link_text = '\n        publish&nbsp;now\n      ' 
        test_condition = 'Version approved.'
        url = self.click_content_link(browser, url, test_condition, content,
                                      link_text, tab_name)
        # now that the document is published, click public view
        link_text = 'view public version'
        test_condition = '<h2 class="heading">test content</h2>'
        url = self.click_content_link(browser, url, test_condition, content,
                                    link_text)
        browser.goBack()
        self.do_logout(browser)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerScenarioOneTestCase))
    return suite
