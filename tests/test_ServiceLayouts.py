# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Testing import ZopeTestCase

ZopeTestCase.installProduct('SilvaInfraeLayouts')


class TestInstallLayouts(SilvaTestCase.SilvaTestCase):

    layoutInfrae1 = 'Infrae1'

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.service_layouts = self.root.service_layouts

    def testSetup(self):
        self.failUnless(hasattr(self.root, 'service_layouts'))
        self.failUnless(hasattr(self.root.service_resources, 'Layouts'))
        self.assertEqual(len(self.service_layouts.get_names()), 2)
        self.failUnless(self.layoutInfrae1 in self.service_layouts.get_names())
        self.assertEqual(len(self.service_layouts.get_installed_names()),0)

    def testInstall(self):
        self.service_layouts.install(self.layoutInfrae1)
        self.assertEqual(len(self.service_layouts.get_installed_names()),1)
        self.failUnless(self.layoutInfrae1 in self.service_layouts.get_installed_names())
        self.failUnless(self.service_layouts.is_installed(self.layoutInfrae1))
        self.failUnless(hasattr(self.root.service_resources.Layouts, self.layoutInfrae1))

    def testUninstall(self):
        self.service_layouts.install(self.layoutInfrae1)
        self.service_layouts.uninstall(self.layoutInfrae1)
        self.assertEqual(len(self.service_layouts.get_installed_names()),0)
        self.failIf(self.layoutInfrae1 in self.service_layouts.get_installed_names())
        self.failIf(self.service_layouts.is_installed(self.layoutInfrae1))

class TestServiceLayouts(SilvaTestCase.SilvaTestCase):

    layoutInfrae1 = 'Infrae1'
    layoutInfrae2b = 'Infrae2b'
    layoutInfrae1Items = ['content.html', 'layout_macro.html', 'template']

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.service_layouts = self.root.service_layouts
        self.service_layouts.install(self.layoutInfrae1)
        self.service_layouts.install(self.layoutInfrae2b)

    def testSetupInPublication(self):
        self.add_publication(self.root, 'pub', 'publication')
        self.failUnless(self.root.pub)
        self.pub = self.root.pub
        self.failIf(self.service_layouts.layout_items(self.pub))     
        # setup layout
        self.service_layouts.setup_layout(self.layoutInfrae1, self.pub)
        for id in self.layoutInfrae1Items:
            self.failUnless(id in self.pub.objectIds())
        self.failUnless(self.service_layouts.has_layout(self.pub))
        for id in self.layoutInfrae1Items:
            self.failUnless(id in self.service_layouts.layout_items(self.pub))     
        
        # remove layout
        self.service_layouts.remove_layout(self.pub)
        self.failIf(self.service_layouts.has_layout(self.pub))
        self.failIf(self.service_layouts.layout_items(self.pub))     
        for id in self.layoutInfrae1Items:
            self.failIf(id in self.pub.objectIds())

    def testSetupOnPublication(self):
        self.add_publication(self.root, 'pub', 'publication')
        self.failUnless(self.root.pub)
        self.pub = self.root.pub
        self.pub.set_layout(self.layoutInfrae2b)
        self.pub.set_layout(self.layoutInfrae1)

        for id in self.layoutInfrae1Items:
            self.failUnless(id in self.pub.objectIds())
        self.failUnless(self.service_layouts.has_layout(self.pub))
        for id in self.layoutInfrae1Items:
            self.failUnless(id in self.service_layouts.layout_items(self.pub))     
        

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestInstallLayouts))
        suite.addTest(unittest.makeSuite(TestServiceLayouts))
        return suite

