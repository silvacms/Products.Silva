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
        test_condition = 'kupu editor'
        browser.open(base_url)
        self.click_content_tab_name(browser, base_url, test_condition, content,
                                          tab_name)
        # click on the preview tab
        tab_name = 'tab_preview'
        test_condition = 'public&nbsp;preview...'
        self.click_content_tab_name(browser, base_url, test_condition, content,
                                          tab_name)
        # click the public view link
        link_text = 'view public version'
        test_condition = 'Sorry, this Silva Document is not viewable.'
        self.click_content_no_tab_name(browser, base_url, test_condition, content,
                                             link_text)
        # oops, document not viewable, go back to public preview
        browser.goBack()
        #url = browser.url
        self.failUnless('public&nbsp;preview' in browser.contents)
        self.failUnless('<h2 class="heading">test content€</h2>' in browser.contents)
        # click publish now button
        tab_name = 'quick_publish?return_to=tab_preview'
        test_condition = 'Version approved.'
        self.click_content_tab_name(browser, base_url, test_condition, content,
                                          tab_name)
        # now that the document is published, click public view
        link_text = 'view public version'
        test_condition = '<h2 class="heading">test content€</h2>'
        self.click_content_no_tab_name(browser, base_url, test_condition, content,
                                    link_text)
        # go back to preview page
        browser.goBack()
        # click root link
        tab_name = 'tab_edit'
        test_condition = '&#xab;root&#xbb;'
        self.click_tab_name(browser, base_url, test_condition, tab_name)
        # check test_content and close
        browser.getControl(name='ids:list').value = ['test_content']
        browser.getControl(name='tab_edit_close:method').click()
        self.failUnless('test_content' in browser.contents)
        # delete content
        self.do_delete_content(browser)
        # logout
        self.do_logout(browser)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerScenarioOneTestCase))
    return suite
