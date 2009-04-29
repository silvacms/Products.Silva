import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class ManagerPropertiesSilvaRootTestCase(SilvaFunctionalTestCase):
    """
        test properties tabs 'settings...' and 'addables...' as manager
    """

    def test_manager_properties_silvaroot(self):
        sb = SilvaBrowser()
        status, url = sb.login('manager', 'secret', sb.smi_url())
        self.assertEquals(status, 200)
        sb.click_tab_named('properties')
        sb.click_button_labeled('addables...')
        field = sb.browser.getControl(name='field_acquire_addables')
        field.value = False
        fields = sb.browser.getControl(name='field_addables')
        fields.value = []
        sb.click_button_labeled('save addables settings')
        field = sb.browser.getControl(name='field_acquire_addables')
        self.assertEquals(field.value, False)
        fields = sb.browser.getControl(name='field_addables')
        self.assertEquals(fields.value, [])
        status, url = sb.click_href_labeled('logout')
        self.assertEquals(status, 401)        # doesn't work!?!
                                              # does work(?) logout
                                              # results in 401

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerPropertiesSilvaRootTestCase))
    return suite
