import os.path
from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

def openFile(filename):
    name = os.path.dirname(__file__)
    return open(name + '/data/' + filename)

class ManagerImageTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                           MixinRoleContent, MixinNavigate,
                           MixinFieldParameters):
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

    def afterSetUp(self):
        self.setUpMixin()

    def smi_url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url

    def test_manager_image(self):
        base_url = self.smi_url()
        base = None
        browser = Browser()
        # login
        self.role_login_edit(browser, SilvaTestCase.user_manager, success,
                             base=base)
        # create silva document
        self.do_create_content(browser, 'Silva Image',
                               self.fill_create_image_fields, success)
        # click on image
        content = 'test_content'
        tab_name = 'tab_edit'
        test_condition = 'format and scaling'
        url = self.click_content_tab_name(browser, base_url, test_condition, content,
                                          tab_name)
        # change field image title
        browser.getControl(name='field_image_title').value = 'new test content€'
        browser.getControl(name='submit:method').click()
        self.failUnless('Properties changed' in browser.contents)
        # change image type
        browser.getControl(name='field_web_format').value = ['PNG']
        browser.getControl(name='scale_submit:method').click()
        self.failUnless('Scaling and/or format changed' in browser.contents)
        # scale image by 100x200
        browser.getControl(name='field_web_scaling').value = '100x200'
        browser.getControl(name='scale_submit:method').click()
        self.failUnless('Scaling and/or format changed' in browser.contents)
        # scale image by 40%
        browser.getControl(name='field_web_scaling').value = '80%'
        browser.getControl(name='scale_submit:method').click()
        self.failUnless('Scaling and/or format changed' in browser.contents)
        # click on view unscaled image
        # click on upload a file
        browser.getControl(name='field_file').add_file(openFile('torvald.jpg'), 'image/jpeg', 'torvald.jpg')
        browser.getControl(name='upload_submit:method').click()
        self.failUnless('Image updated.' in browser.contents)
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
    suite.addTest(unittest.makeSuite(ManagerImageTestCase))
    return suite
