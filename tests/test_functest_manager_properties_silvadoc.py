from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

class ManagerPropertiesSilvaDocTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                        MixinRoleContent, MixinNavigate,
                                        MixinFieldParameters):
    """
        login manager
        select silva document
        make silva document
        click properties tab
        fill in all property fields
        submit
    """

    def afterSetUp(self):
        self.setUpMixin()

    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

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
        # click into the silva document
        content = 'test_content'
        tab_name = 'tab_edit'
        test_condition = 'kupu editor'
        self.click_content_tab_name(browser, base_url, test_condition, content,
                                          tab_name)
        # click on the properties button
        tab_name = 'tab_metadata'
        test_condition = 'settings...'
        self.click_content_tab_name(browser, base_url, test_condition, content,
                                          tab_name)
        # submit index 0
        # fill fields 
        browser.getControl(name='silva-content.maintitle:record').value = 'test content€ new'
        browser.getControl(name='silva-content.shorttitle:record').value = 'test content€ shorttitle'
        # click submit
        browser.getControl(name='save_metadata:method', index=0).click()
        # test fields
        self.failUnless('test content€ new' in browser.contents)
        self.failUnless('test content€ shorttitle' in browser.contents)
        # submit index 1
        # fill fields
        browser.getControl(name='silva-extra.subject:record').value = 'test content€ subject'
        browser.getControl(name='silva-extra.keywords:record').value = 'keyword€1 keyword€2'
        browser.getControl(name='silva-extra.content_description:record').value = 'keyword€1 keyword€2 keyword€1 keyword€2'
        browser.getControl(name='silva-extra.comment:record').value = 'comment€ comment€ comment€ comment€'
        browser.getControl(name='silva-extra.contactname:record').value = 'test name€'
        browser.getControl(name='silva-extra.contactemail:record').value = 'testemail@example.com'
        browser.getControl(name='silva-extra.hide_from_tocs:record').value = ['hide']
        # click submit
        browser.getControl(name='save_metadata:method', index=1).click()
        # test fields
        self.failUnless('test content€ subject' in browser.contents)
        self.failUnless('keyword€1 keyword€2' in browser.contents)
        self.failUnless('keyword€1 keyword€2 keyword€1 keyword€2' in browser.contents)
        self.failUnless('comment€ comment€ comment€ comment€' in browser.contents)
        self.failUnless('test name€' in browser.contents)
        self.failUnless('testemail@example.com' in browser.contents)
        self.failUnless('checked="checked"' in browser.contents)
        # language
        browser.getControl(name='silva-extra.language:record').value = ['ab']
        browser.getControl(name='save_metadata:method', index=1).click()
        browser.getControl(name='silva-extra.language:record').value
        f = browser.getControl('Abkhazian').selected
        self.assertEquals(f, True)
        # click root link
        tab_name = 'tab_edit'
        test_condition = '&#xab;root&#xbb;'
        self.click_tab_name(browser, base_url, test_condition, tab_name)
        # check test_content and close
        browser.getControl(name='ids:list').value = ['test_content']
        browser.getControl(name='tab_edit_close:method').click()
        # delete content
        self.do_delete_content(browser)
        # logout
        self.do_logout(browser)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerPropertiesSilvaDocTestCase))
    return suite
