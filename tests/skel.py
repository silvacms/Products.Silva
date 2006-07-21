#
# Example SilvaTestCase
#
import SilvaTestCase

class TestSilvaTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        pass

    def test_hasRoot(self):
        assert hasattr(self.app, 'root')


def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSilvaTestCase))
    return suite

