from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

class ManagerPropertiesSilvaFolderTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                   MixinRoleContent, MixinNavigate,
                                   MixinFieldParameters):
    """
        as manager change the properties of a folder for the settings page
    """

    def afterSetUp(self):
        self.setUpMixin()

    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

    def test_manager_properties_folder(self):
        base_url = self.smi_url()
        base = None
        browser = Browser()
        # login
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        # create silva folder
        self.do_create_content(browser, 'Silva Folder',
                               self.fill_create_title_field, success)
        # click into the silva folder
        content = 'test_content'
        tab_name = 'tab_edit'
        test_condition = '&#xab;test content€&#xbb;'
        self.click_content_tab_name(browser, base_url, test_condition, content,
                                    tab_name)
        # click on the properties button
        tab_name = 'tab_metadata'
        test_condition = 'settings...'
        self.click_content_tab_name(browser, base_url, test_condition, content,
                                          tab_name)
        # click on the settings button
        tab_name = 'tab_settings'
        test_condition = 'settings for '
        self.click_content_tab_name(browser, base_url, test_condition, content,
                                          tab_name)
        # click convert to publication
        browser.getControl(name='tab_edit_to_publication:method').click()
        self.failUnless('Changed into publication' in browser.contents)
        # click convert to folder
        browser.getControl(name='tab_edit_to_folder:method').click()
        self.failUnless('Changed into folder' in browser.contents)
        # click rss feed checkbox
        browser.getControl(name='allow_feeds').value = ['checked']
        browser.getControl(name='tab_settings_save_feeds:method').click()
        self.failUnless('Feed settings saved.' in browser.contents)
        # click root link
        tab_name = 'tab_edit'
        test_condition = '&#xab;root&#xbb;'
        self.click_tab_name(browser, base_url, test_condition, tab_name)
        # delete content
        self.do_delete_content(browser)
        # logout
        self.do_logout(browser)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerPropertiesSilvaFolderTestCase))
    return suite
