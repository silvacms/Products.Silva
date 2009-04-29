import unittest
from SilvaTestCase import SilvaFunctionalTestCase
from SilvaBrowser import SilvaBrowser

class MyFunctionalTest(SilvaFunctionalTestCase):
    """
    this is a test example
    login
    test login success
    make silva document
    test existence of the document
    select and delet the document
    test deletion
    logout
    test logout
    """
    
    def test_example(self):
        # get the SilvaBrowser
        sb = SilvaBrowser()
        # login as manager
        status, url = sb.login('manager', 'secret', sb.smi_url())
        # test login success
        self.assertEquals(status, 200)
        # make silva document
        sb.make_content('Silva Document', id='test_document',
                                          title='Test document')
        # test existence of document
        data = sb.get_content_data()
        self.assertEquals(data[1]['name'], u'Test document')
        # select and delete content
        sb.select_delete_content('test_document')
        # test deletion
        self.failUnless('test_document' in sb.browser.contents)
        # logout
        status, url = sb.click_href_labeled('logout')
        # test logout status
        self.assertEquals(status, 401)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MyFunctionalTest))
    return suite
