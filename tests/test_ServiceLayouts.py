# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_ServiceLayouts.py,v 1.5 2003/10/15 19:24:30 gotcha Exp $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
    moduleFilename = sys.argv[0]
else:
    moduleFilename = __file__
moduleFilename = os.path.abspath(moduleFilename)    
modulePathname = os.path.dirname(moduleFilename)
    
import SilvaTestCase
from Testing import ZopeTestCase


from Products.Silva.LayoutRegistry import layoutRegistry
from Products.Silva.LayoutService import LayoutService
from Products.Silva.fssite import registerDirectory


layoutTest1 = {'name':'test1', 'directory':'layout_test1', 'description':'test 1 Layout'}
layoutTest2 = {'name':'test2', 'directory':'layout_test2', 'description':'test 2 Layout'}

layoutTest1Items = ['template', 'test1.html']
layoutTest2Items = ['template', 'test2.html']

layoutRegistry.register(layoutTest1['name'], layoutTest1['description'],
    moduleFilename, layoutTest1['directory'])
layoutRegistry.register(layoutTest2['name'], layoutTest2['description'],
    moduleFilename, layoutTest2['directory'])

from Products.Silva import Publication, Root
# XXX ugh, awful monkey patch
Publication.Publication.cb_isMoveable = lambda self: 1
# manage_main hacks to copy succeeds
Root.Root.manage_main = lambda *foo, **bar: None

class TestInstallLayouts(SilvaTestCase.SilvaTestCase):


    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.service_layouts = self.root.service_layouts

    def testSetup(self):
        self.failUnless(hasattr(self.root, 'service_layouts'))
        self.failUnless(hasattr(self.root.service_resources, 'Layouts'))
        self.assertEqual(len(self.service_layouts.get_names()), 2)
        self.failUnless(layoutTest1['name'] in self.service_layouts.get_names())
        self.assertEqual(len(self.service_layouts.get_installed_names()),0)

    def testInstall(self):
        self.service_layouts.install(layoutTest1['name'])
        self.assertEqual(len(self.service_layouts.get_installed_names()),1)
        self.failUnless(layoutTest1['name'] in self.service_layouts.get_installed_names())
        self.failUnless(self.service_layouts.is_installed(layoutTest1['name']))
        self.failUnless(hasattr(self.root.service_resources.Layouts, layoutTest1['directory']))
        select = self.service_layouts.get_installed_for_select()
        self.assertEqual(len(select), 3)
        awaited = [(LayoutService.NOLAYOUT, ''), (layoutTest1['description'], layoutTest1['name']), (layoutTest2['description'], layoutTest2['name'])]
        for item in awaited:
            self.failUnless(item in select)
        
    def testUninstall(self):
        self.service_layouts.install(layoutTest1['name'])
        self.service_layouts.uninstall(layoutTest1['name'])
        self.assertEqual(len(self.service_layouts.get_installed_names()),0)
        self.failIf(layoutTest1['name'] in self.service_layouts.get_installed_names())
        self.failIf(self.service_layouts.is_installed(layoutTest1['name']))

class TestServiceLayouts(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.service_layouts = self.root.service_layouts
        self.service_layouts.install(layoutTest1['name'])
        self.service_layouts.install(layoutTest2['name'])

    def testSetupInPublication(self):
        self.add_publication(self.root, 'pub', 'publication')
        self.failUnless(self.root.pub)
        self.pub = self.root.pub
        self.failIf(self.service_layouts.layout_items(self.pub))     
        # setup layout
        self.service_layouts.setup_layout(layoutTest1['name'], self.pub)
        for id in layoutTest1Items:
            self.failUnless(id in self.pub.objectIds())
        self.failUnless(self.service_layouts.has_layout(self.pub))
        for id in layoutTest1Items:
            self.failUnless(id in self.service_layouts.layout_items(self.pub))
        # remove layout
        self.service_layouts.remove_layout(self.pub)
        self.failIf(self.service_layouts.has_layout(self.pub))
        self.failIf(self.service_layouts.layout_items(self.pub))     
        for id in layoutTest1Items:
            self.failIf(id in self.pub.objectIds())

    def testSetupOnPublication(self):
        self.add_publication(self.root, 'pub', 'publication')
        self.failUnless(self.root.pub)
        self.pub = self.root.pub
        self.pub.set_layout(layoutTest2['name'])
        self.pub.set_layout(layoutTest1['name'])
        self.checkLayoutTest1(self.pub)
        self.pub.set_layout('')
        self.failIf(self.service_layouts.has_layout(self.pub))

    def checkLayoutTest1(self, pub):
        for id in layoutTest1Items:
            self.failUnless(id in pub.objectIds())
        self.failUnless(self.service_layouts.has_layout(pub))
        for id in layoutTest1Items:
            self.failUnless(id in self.service_layouts.layout_items(pub))

    def checkLayoutTest2(self, pub):
        for id in layoutTest2Items:
            self.failUnless(id in pub.objectIds())
        self.failUnless(self.service_layouts.has_layout(pub))
        for id in layoutTest2Items:
            self.failUnless(id in self.service_layouts.layout_items(pub))

    def testCopyPaste(self):        
        self.add_publication(self.root, 'pub', 'publication')
        self.failUnless(self.root.pub)
        self.pub = self.root.pub
        self.pub.set_layout(layoutTest1['name'])
        self.checkLayoutTest1(self.pub)
        self.root.action_copy(['pub'], self.app.REQUEST)
        self.root.action_paste(self.app.REQUEST)
        self.failUnless(self.root.copy_of_pub)
        self.copy_of_pub = self.root.copy_of_pub
        self.copy_of_pub.set_layout(layoutTest2['name'])
        self.checkLayoutTest1(self.pub)
        self.checkLayoutTest2(self.copy_of_pub)
        self.pub.set_layout(layoutTest2['name'])
        self.checkLayoutTest2(self.pub)

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

