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
        fields = sb.browser.getControl(name='field_addables')
        fields.value = []
        sb.click_button_labeled('save addables settings')
        
        #form = sb.browser.getForm(name='form')
        #field = form.getControl(name='field_addables')       
        # uncheck the checked boxes
        # XXX
        # seems the only way i can use selected is by a label name, however the
        # fields on this page have been built in formulator which doesn't make
        # label tags. been trying to use selected by a checkbox name, but that
        status, url = sb.click_href_labeled('logout')
        self.assertEquals(status, 401)        # doesn't work!?!

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ManagerPropertiesSilvaRootTestCase))
    return suite
