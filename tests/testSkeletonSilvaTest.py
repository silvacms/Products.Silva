# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
import SilvaTestCase


class TestSomeProduct(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        pass

    def testSomething(self):
        '''Test something'''
        self.failUnless(1==1)

            
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestSomeProduct))
        return suite

