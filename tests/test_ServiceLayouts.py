# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Testing import ZopeTestCase

ZopeTestCase.installProduct('SilvaInfraeLayouts')


class TestServiceLayouts(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        pass 

    def testSetup(self):
        self.failUnless(hasattr(self.root, 'service_layouts'))
        self.failUnless(hasattr(self.root.service_resources, 'Layouts'))
        self.assertEqual(len(self.root.service_layouts.get_names()), 2)
        self.failUnless('Infrae1' in self.root.service_layouts.get_names())
        self.assertEqual(len(self.root.service_layouts.get_installed_names()),0)

    def testInstall(self):
        self.setRoles(['Manager'])
        self.service_layouts = self.root.service_layouts
        self.service_layouts.install('Infrae1')
        self.assertEqual(len(self.service_layouts.get_installed_names()),1)
        self.failUnless('Infrae1' in self.service_layouts.get_installed_names())
        self.failUnless(self.service_layouts.is_installed('Infrae1'))
        self.failUnless(hasattr(self.root.service_resources.Layouts,'Infrae1'))

    def testUninstall(self):
        self.setRoles(['Manager'])
        self.service_layouts = self.root.service_layouts
        self.service_layouts.install('Infrae1')
        self.service_layouts.uninstall('Infrae1')
        self.assertEqual(len(self.service_layouts.get_installed_names()),0)
        self.failIf('Infrae1' in self.service_layouts.get_installed_names())
        self.failIf(self.service_layouts.is_installed('Infrae1'))
        
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestServiceLayouts))
        return suite

