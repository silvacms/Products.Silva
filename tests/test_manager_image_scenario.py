from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

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
        self.failUnless('Scaling and/or format changed')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerImageTestCase))
    return suite
