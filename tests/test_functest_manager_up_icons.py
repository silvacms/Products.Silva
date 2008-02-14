from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

class ManagerUpIconsTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                             MixinRoleContent, MixinNavigate,
                             MixinFieldParameters):
    """
       login manager
       select image folder
       make silva folder
       enter folder
       for each tab type
       click up_tree
       enter folder
       for each tab type
       click up level
       delete folder
       logout
    """

    def afterSetUp(self):
        self.setUpMixin()
    
    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

    def test_manager_level_icons(self):
        base_url = self.smi_url()
        base = None
        browser = Browser()
        # login
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        # create silva folder
        self.do_create_content(browser, 'Silva Folder',
                               self.fill_create_folderish_field, success)
        # click on folder
        content = 'test_content'
        tab_name = 'tab_edit'
        test_condition = 'test_content'
        url = self.click_content_tab_name(browser, base_url, test_condition, content,
                                          tab_name)
        # create silva folder
        self.do_create_content(browser, 'Silva Folder',
                               self.fill_create_folderish_field, success)
        base_url = url.split('/')
        base_url.insert(4, 'test_content')
        base_url = '/'.join(base_url)
        self.content_link_builder(content, tab_name)
        # click on folder
        link = browser.getLink(url=base_url)
        link.click()
        link = browser.getLink('index')
        # check we are two level deep
        self.assertEquals(link.text, 'index')
        # get level up icon
        link = browser.getLink(id='level_up')
        # check we have the content level_up link
        self.assertEquals(link.url, 'http://nohost/root/test_content/edit/tab_edit')
        # click level up icon
        link.click()
        # get tree up icon
        link = browser.getLink(id='tree_up')
        # check we have the content tree_up link
        self.assertEquals(link.url, 'http://nohost/root/edit/tab_edit')
        # click tree up icon
        link.click()
        self.failUnless('&#xab;root&#xbb;' in browser.contents)
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
    suite.addTest(unittest.makeSuite(ManagerUpIconsTestCase))
    return suite
