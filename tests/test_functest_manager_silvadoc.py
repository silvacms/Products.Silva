import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class ManagerScenarioOneTestCase(SilvaFunctionalTestCase):
                                 
    """
        login manager
        select test_document
        make test_document
        enter test_document
        click preview tab
        click public view
        click back
        click publish now tab
        click public view
        click back
        close test_document
        delete test_document
        logout
    """

    def test_manager_scenario_one(self):
        sb = SilvaBrowser()
        sb.login('manager', 'secret', sb.smi_url())
        sb.make_content('Silva Document', id='test_document',
                                          title='Test document')
        sb.click_href_labeled('test_document')
        sb.click_tab_named('preview')
        sb.click_href_labeled('view public version')
        self.failUnless('Sorry, this Silva Document is not viewable' in sb.browser.contents)
        sb.browser.goBack()
        self.failUnless('public&nbsp;preview' in sb.browser.contents)
        self.failUnless('<h2 class="heading">Test document</h2>' in sb.browser.contents)
        status, url = sb.click_button_labeled('publish now')
        self.failUnless(sb.get_status_feedback().startswith('Version approved.'))
        sb.click_href_labeled('view public version')
        sb.browser.goBack()
        self.failUnless(sb.get_status_feedback().startswith('Version approved.'))
        sb.click_href_labeled('root')
        sb.click_tab_named('contents')
        sb.select_content('test_document')
        status, url = sb.click_button_labeled('close')
        self.failUnless(sb.get_status_feedback().startswith('Closed'))
        sb.select_delete_content('test_document')
        status, url = sb.click_href_labeled('logout')
        self.assertEquals(status, 401)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerScenarioOneTestCase))
    return suite