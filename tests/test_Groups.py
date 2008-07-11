# Copyright (c) 2003-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $
import SilvaTestCase

class GroupTestCase(SilvaTestCase.SilvaTestCase):

    def test_create(self):
        pass


class IPGroupTestCase(SilvaTestCase.SilvaTestCase):

    def test_create(self):
        pass

class VirtualGroupTestCase(SilvaTestCase.SilvaTestCase):

    def test_create(self):
        pass


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GroupTestCase))
    suite.addTest(unittest.makeSuite(IPGroupTestCase))
    suite.addTest(unittest.makeSuite(VirtualGroupTestCase))
    return suite
    
