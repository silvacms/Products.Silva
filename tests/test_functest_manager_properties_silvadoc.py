import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class ManagerPropertiesSilvaDocTestCase(SilvaFunctionalTestCase):
    """
        login manager
        select silva document
        make silva document
        click properties tab
        fill in all property fields
        submit
    """

    def test_manager_properties(self):
        sb = SilvaBrowser()
        # login
        status, url = sb.login('manager', 'secret', sb.smi_url())
        self.assertEquals(status, 200)
        sb.make_content('Silva Document', id='test_document',
                                          title='Test document')
        self.failUnless('test_document' in sb.get_content_ids())
        # click into the silva document
        sb.click_href_labeled('test_document')
        tab_name = sb.get_tabs_named('editor')
        self.assertEquals(tab_name, 'editor')
        sb.click_tab_named('properties')
        self.assertEquals(sb.browser.url,
                          'http://nohost/root/test_document/edit/tab_metadata')
        tab_name = sb.get_middleground_buttons('settings...')
        self.failUnless(tab_name, 'settings...')
        
        ## fill fields 
        sb.browser.getControl(name='silva-content.maintitle:record').value = 'test content€ new'
        sb.browser.getControl(name='silva-content.shorttitle:record').value = 'test content€ shorttitle'
        sb.browser.getControl(name='save_metadata:method', index=0).click()
        self.failUnless('test content€ new' in sb.browser.contents)
        self.failUnless('test content€ shorttitle' in sb.browser.contents)
        sb.browser.getControl(name='silva-extra.subject:record').value = 'test content€ subject'
        sb.browser.getControl(name='silva-extra.keywords:record').value = 'keyword€1 keyword€2'
        sb.browser.getControl(name='silva-extra.content_description:record').value = 'keyword€1 keyword€2 keyword€1 keyword€2'
        sb.browser.getControl(name='silva-extra.comment:record').value = 'comment€ comment€ comment€ comment€'
        sb.browser.getControl(name='silva-extra.contactname:record').value = 'test name€'
        sb.browser.getControl(name='silva-extra.contactemail:record').value = 'testemail@example.com'
        sb.browser.getControl(name='silva-extra.hide_from_tocs:record').value = ['hide']
        sb.browser.getControl(name='save_metadata:method', index=1).click()
        self.failUnless('test content€ subject' in sb.browser.contents)
        self.failUnless('keyword€1 keyword€2' in sb.browser.contents)
        self.failUnless('keyword€1 keyword€2 keyword€1 keyword€2' in sb.browser.contents)
        self.failUnless('comment€ comment€ comment€ comment€' in sb.browser.contents)
        self.failUnless('test name€' in sb.browser.contents)
        self.failUnless('testemail@example.com' in sb.browser.contents)
        self.failUnless('checked="checked"' in sb.browser.contents)
        sb.browser.getControl(name='silva-extra.language:record').value = ['ab']
        sb.browser.getControl(name='save_metadata:method', index=1).click()
        sb.browser.getControl(name='silva-extra.language:record').value
        f = sb.browser.getControl('Abkhazian').selected
        self.assertEquals(f, True)
        sb.go(sb.smi_url())
        data = sb.get_content_data()
        self.assertEquals(data[1]['id'], u'test_document')
        sb.select_delete_content('test_document')
        data = sb.get_content_ids()
        self.failIf('test_document' in data)
        status, url = sb.click_href_labeled('logout')
        self.assertEquals(status, 401)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerPropertiesSilvaDocTestCase))
    return suite
        
