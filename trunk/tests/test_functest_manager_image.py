import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class ManagerImageTestCase(SilvaFunctionalTestCase):
    """
        login manager
        select silva image
        make silva image
        click silva image
        test fields
        submit
        delete content
        logout
    """

    def test_manager_image(self):
        sb = SilvaBrowser()
        status, url = sb.login('manager', 'secret', sb.smi_url())
        self.assertEquals(status, 200)
        sb.make_content('Silva Image', id='test_image', title='Test image',
                        image='torvald.jpg')
        data = sb.get_content_data()
        self.assertEquals(data[1]['name'], u'Test image')
        sb.click_href_labeled('test_image')
        sb.browser.getControl(name='field_image_title').value = 'new test content€'
        sb.browser.getControl(name='submit:method').click()
        self.failUnless('Properties changed' in sb.browser.contents)
        sb.browser.getControl(name='field_web_format').value = ['PNG']
        sb.browser.getControl(name='scale_submit:method').click()
        self.failUnless('Scaling and/or format changed' in sb.browser.contents)
        sb.browser.getControl(name='field_web_scaling').value = '100x200'
        sb.browser.getControl(name='scale_submit:method').click()
        self.failUnless('Scaling and/or format changed' in sb.browser.contents)
        sb.browser.getControl(name='field_file').add_file(
                   sb.open_file('torvald.jpg'), 'image/jpeg', 'torvald.jpg')
        sb.browser.getControl(name='upload_submit:method').click()
        self.failUnless('Image updated.' in sb.browser.contents)
        sb.go(sb.smi_url())
        sb.select_delete_content('test_image')
        self.failUnless('test_image' in sb.browser.contents)
        status, url = sb.click_href_labeled('logout')
        self.assertEquals(status, 401)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerImageTestCase))
    return suite
