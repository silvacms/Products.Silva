import unittest

from SilvaTestCase import SilvaFunctionalTestCase
from SilvaBrowser import SilvaBrowser

class ManagerUserSettingsTestCase(SilvaFunctionalTestCase):
    """
    """

    def test_manager_user_settings(self):
        sb = SilvaBrowser()
        # login
        sb.login('manager', 'secret', sb.smi_url())
        sb.click_href_labeled('user settings')
        form = sb.browser.getForm(name='user_settings_form')
        form.getControl(name='field_fullname').value = 'test_bill'
        form.getControl(name='field_email').value = 'test@example.com'
        form.getControl(name='langsetting').value = ['it']
        form.getControl(name='field_editor').value = ['forms editor']
        form.getControl(name='save_memberdata:method').click()
        self.assertEquals(sb.browser.getControl(name='field_fullname').value, 'test_bill')
        self.assertEquals(sb.browser.getControl(name='field_email').value, 'test@example.com')
        f = sb.browser.getControl('italiano').selected
        self.assertEquals(f, True)
        f = sb.browser.getControl('forms editor').selected
        self.assertEquals(f, True)
        form = sb.browser.getForm(name='user_settings_form')
        # XXX js onclick to close!!!
        # so i just 'hard' logout via the zmi
        sb.logout()
        self.failUnless('You have been logged out.' in sb.browser.contents)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerUserSettingsTestCase))
    return suite
