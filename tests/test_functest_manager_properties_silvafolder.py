import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class ManagerPropertiesSilvaFolderTestCase(SilvaFunctionalTestCase):
    """
        as manager change the properties of a folder for the settings page
    """

    def test_manager_properties_folder(self):
        sb = SilvaBrowser()
        # login
        sb.login('manager', 'secret', sb.smi_url())
        # create silva folder
        sb.make_content('Silva Folder', id='test_folder', title='Test folder',
                        policy='Silva Document')
        data = sb.get_content_ids()
        self.failUnless('test_folder' in data)
        sb.click_href_labeled('test_folder')
        self.assertEquals(sb.browser.url,
                          'http://nohost/root/test_folder/edit/tab_edit')
        sb.click_tab_named('properties')
        tab_name = sb.get_middleground_buttons('settings...')
        self.assertEquals(tab_name, 'settings...')
        sb.click_tab_named('settings...')
        self.assertEquals(sb.browser.url,
                          'http://nohost/root/test_folder/edit/tab_settings')
        ## click convert to publication
        sb.browser.getControl(name='tab_edit_to_publication:method').click()
        self.failUnless('Changed into publication' in sb.browser.contents)
        ## click convert to folder
        sb.browser.getControl(name='tab_edit_to_folder:method').click()
        self.failUnless('Changed into folder' in sb.browser.contents)
        ## click rss feed checkbox
        sb.browser.getControl(name='allow_feeds').value = ['checked']
        sb.browser.getControl(name='tab_settings_save_feeds:method').click()
        self.failUnless('Feed settings saved.' in sb.browser.contents)
        sb.go(sb.smi_url())
        sb.select_delete_content('test_folder')
        sb.click_href_labeled('logout')
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerPropertiesSilvaFolderTestCase))
    return suite
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
