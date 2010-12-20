import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class ContentNotAddableCase(SilvaFunctionalTestCase):
    def test_reader(self):
        sb = SilvaBrowser()
        # test that a reader cannot add anything
        sb.login('reader', url=sb.smi_url())
        self.assertEquals(sb.get_addables_list(), [])
        sb.logout()

    def test_author_publication(self):
        sb = SilvaBrowser()
        sb.login('author', url=sb.smi_url())
        self.failIf('Silva Publication' in sb.get_addables_list())
        sb.logout()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentNotAddableCase))
    return suite
