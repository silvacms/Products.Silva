#
# Example SilvaTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase

class TestSilvaTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        pass

    def test_hasRoot(self):
        assert hasattr(self.app, 'root')


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestSilvaTestCase))
        return suite

