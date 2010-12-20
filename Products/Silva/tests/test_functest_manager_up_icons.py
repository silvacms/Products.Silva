import unittest

from SilvaTestCase import SilvaFunctionalTestCase
from SilvaBrowser import SilvaBrowser

class ManagerUpIconsTestCase(SilvaFunctionalTestCase):
    """
       login manager
       select silva folder
       make test_folder1
       enter test_folder1
       select silva folder
       make test_folder2
       enter test_folder2
       click up_tree
       re-enter test_folder2
       click up_level
       click up_tree
       select test_folder1
       delete test_folder1
       logout
    """

    def test_manager_level_icons(self):
        sb = SilvaBrowser()
        sb.login('manager', 'secret', sb.smi_url())
        sb.make_content('Silva Folder', id='test_folder1',
                                        title='Test folder1',
                                        policy='Silva Document')
        sb.click_href_labeled('test_folder1')
        h2 = sb.get_listing_h2()
        self.failUnless(h2.startswith('Silva Folder '))
        sb.make_content('Silva Folder', id='test_folder2',
                                        title='Test folder2',
                                        policy='Silva Document')
        sb.click_href_labeled('test_folder2')
        h2 = sb.get_listing_h2()
        self.failUnless(h2.startswith('Silva Folder '))
        link = sb.browser.getLink(url='http://nohost/root/edit/tab_edit')
        link.click()
        h2 = sb.get_listing_h2()
        self.failUnless(h2.startswith('Silva Root '))
        sb.click_href_labeled('test_folder1')
        sb.click_href_labeled('test_folder2')
        h2 = sb.get_listing_h2()
        self.failUnless('Test folder2' in h2)
        link = sb.browser.getLink(url='http://nohost/root/test_folder1/edit/tab_edit')
        link.click()
        h2 = sb.get_listing_h2()
        self.failUnless('Test folder1' in h2)
        sb.click_href_labeled('root')
        h2 = sb.get_listing_h2()
        self.failUnless(h2.startswith('Silva Root'))
        status, url =sb.select_delete_content('test_folder1')
        self.failUnless(sb.get_status_feedback().startswith('Deleted'))
        status, url = sb.click_href_labeled('logout')
        self.assertEquals(status, 401)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerUpIconsTestCase))
    return suite
