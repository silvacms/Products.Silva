# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_ServiceLayouts.py,v 1.11 2003/11/10 17:08:50 gotcha Exp $

import os, sys
if __name__ == '__main__':
    moduleFilename = os.path.join(os.getcwd(), sys.argv[0])
    execfile(os.path.join(sys.path[0], 'framework.py'))
else:
    moduleFilename = os.path.abspath(__file__)
modulePathname = os.path.dirname(moduleFilename)
    
import SilvaTestCase
from Testing import ZopeTestCase


from Products.Silva.LayoutRegistry import layoutRegistry
from Products.Silva.LayoutService import LayoutService


layoutTest1 = {'name':'test1', 'directory':'layout_test1', 'description':'test 1 Layout'}
layoutTest2 = {'name':'test2', 'directory':'layout_test2', 'description':'test 2 Layout'}

layoutTest1Items = [('template', 'Filesystem Directory View', 'Folder'),
    ('test1.html', 'Filesystem Page Template', 'Page Template'),
    ('test1.css', 'Filesystem DTML Method', 'DTML Method'),
    ('image.gif', 'Filesystem Image', 'Image')]
layoutTest2Items = [('template', 'Filesystem Directory View', 'Folder'),
    ('test2.html', 'Filesystem Page Template', 'Page Template'),
    ('test2.css', 'Filesystem DTML Method', 'DTML Method'),
    ('image.gif', 'Filesystem Image', 'Image')]

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
        # check fs objects
        directory = getattr(self.root.service_resources.Layouts, layoutTest1['directory'])
        self.assertEqual(directory.meta_type, 'Filesystem Directory View')
        for id, fs_meta_type, meta_type in layoutTest1Items:
            self.failUnless(hasattr(directory, id))
            item = getattr(directory, id)
            self.assertEqual(item.meta_type, fs_meta_type)
        # check list for select HTML UI    
        # with one layout
        select = self.service_layouts.get_installed_for_select()
        self.assertEqual(len(select), 2)
        awaited = [(LayoutService.NOLAYOUT, ''), (layoutTest1['description'], layoutTest1['name'])]
        for item in awaited:
            self.failUnless(item in select)
        # with two layouts
        self.service_layouts.install(layoutTest2['name'])
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
        self.add_publication(self.root, 'pub', 'publication')
        self.pub = self.root.pub

    def checkNoLayout(self, pub):
        self.failIf(self.service_layouts.has_layout(pub))
        self.failIf(pub.get_layout())     
        self.assertEqual(pub.get_layout_folder(), pub)     

    def checkNoOwnLayout(self, pub):
        self.failIf(self.service_layouts.has_own_layout(pub))
        self.failIf(pub.get_own_layout())     

    def checkLayout(self, pub, layoutTest):
        self.assertEqual(self.service_layouts.get_layout_name(pub), layoutTest['name'])
        self.failUnless(self.service_layouts.has_layout(pub))
        self.assertEqual(pub.get_layout(), layoutTest['name']) 
        self.assertEqual(pub.get_layout_description(), layoutTest['description']) 

    def checkOwnLayout(self, pub, layoutTest):
        self.failUnless(self.service_layouts.has_own_layout(pub))
        self.assertEqual(pub.get_own_layout(), layoutTest['name']) 

    def checkCopiedLayoutTest1Removed(self, pub):
        self.failIf(self.service_layouts.has_own_layout(pub))
        for id, fs_meta_type, meta_type in layoutTest1Items:
            self.failIf(id in pub.objectIds())

    def checkCopiedLayoutTest1(self, pub):
        self.checkLayout(pub, layoutTest1)
        for id, fs_meta_type, meta_type in layoutTest1Items:
            self.failUnless(id in pub.objectIds())
            item = getattr(pub, id)
            self.assertEqual(item.meta_type, meta_type, '%s metatype : %s != %s' % (id, item.meta_type, meta_type))
        for id, fs_meta_type, meta_type in layoutTest1Items:
            self.failUnless(id in self.service_layouts.layout_ids(pub))
            
    def testWithoutLayouts(self):
        self.checkNoLayout(self.root)
        self.checkNoOwnLayout(self.root)
        self.checkNoLayout(self.pub)
        self.checkNoOwnLayout(self.pub)
        self.add_publication(self.pub, 'subpub', 'subpublication')
        self.subpub = self.pub.subpub
        self.checkNoLayout(self.subpub)
        self.checkNoOwnLayout(self.subpub)

    def testSetupInPublication(self):
        self.failIf(self.service_layouts.layout_ids(self.pub))     
        # setup layout
        self.service_layouts.setup_layout(layoutTest1['name'], self.pub)
        self.checkLayout(self.pub, layoutTest1)
        self.checkOwnLayout(self.pub, layoutTest1)
        # remove layout
        self.service_layouts.remove_layout(self.pub)
        self.checkNoLayout(self.pub)

    def testLayoutOnRoot(self):
        self.root.set_layout(layoutTest2['name'])
        self.checkLayout(self.root, layoutTest2) 
        self.checkOwnLayout(self.root, layoutTest2)

    def testChangeLayout(self):
        self.pub.set_layout(layoutTest1['name'])
        self.checkLayout(self.pub, layoutTest1) 
        self.checkOwnLayout(self.pub, layoutTest1)
        self.pub.set_layout(layoutTest2['name'])
        self.checkLayout(self.pub, layoutTest2) 
        self.checkOwnLayout(self.pub, layoutTest2)
        self.pub.set_layout('')
        self.checkNoLayout(self.pub) 

    def testSetupOnPublication(self):
        self.failIf(self.pub.get_layout_key())
        self.assertEqual(self.service_layouts.get_layout_name(self.pub), '')
        self.pub.set_layout(layoutTest2['name'])
        self.failUnless(self.pub.get_layout_key())
        self.assertEqual(self.service_layouts.get_layout_name(self.pub), layoutTest2['name'])
        self.pub.set_layout(layoutTest1['name'])
        self.failUnless(self.pub.get_layout_key())
        self.checkLayout(self.pub, layoutTest1)
        self.checkOwnLayout(self.pub, layoutTest1)
        self.pub.set_layout('')
        self.checkNoLayout(self.pub)

    def testLayoutCopied(self):
        #before customize
        self.pub.set_layout(layoutTest1['name'])
        self.failIf(self.service_layouts.layout_copied(self.pub), 'Layout should not have been copied !')
        self.failIf(self.pub.layout_copied(), 'Layout should not have been copied !')
        self.service_layouts.copy_layout(self.pub)
        self.checkCopiedLayoutTest1(self.pub)
        self.failUnless(self.service_layouts.layout_copied(self.pub), 'Layout should have been copied !')
        self.failUnless(self.pub.layout_copied(), 'Layout should have been copied !')
        self.service_layouts.remove_layout(self.pub)
        self.checkCopiedLayoutTest1Removed(self.pub)

    def testLayoutCopiedInSilvaRoot(self):
        #before customize
        self.silva.set_layout(layoutTest1['name'])
        self.failIf(self.service_layouts.layout_copied(self.silva), 'Layout should not have been copied !')
        self.failIf(self.silva.layout_copied(), 'Layout should not have been copied !')
        self.service_layouts.copy_layout(self.silva)
        self.checkCopiedLayoutTest1(self.silva)
        self.failUnless(self.service_layouts.layout_copied(self.silva), 'Layout should have been copied !')
        self.failUnless(self.silva.layout_copied(), 'Layout should have been copied !')
        self.service_layouts.remove_layout(self.silva)
        self.checkCopiedLayoutTest1Removed(self.silva)

    def testCopyPaste(self):        
        self.pub.set_layout(layoutTest1['name'])
        self.checkLayout(self.pub, layoutTest1)
        self.checkOwnLayout(self.pub, layoutTest1)
        self.root.action_copy(['pub'], self.app.REQUEST)
        self.root.action_paste(self.app.REQUEST)
        self.failUnless(self.root.copy_of_pub)
        self.copy_of_pub = self.root.copy_of_pub
        self.checkLayout(self.copy_of_pub, layoutTest1)
        self.checkOwnLayout(self.copy_of_pub, layoutTest1)
        self.copy_of_pub.set_layout(layoutTest2['name'])
        self.checkLayout(self.copy_of_pub, layoutTest2)
        self.checkOwnLayout(self.copy_of_pub, layoutTest2)
        self.checkLayout(self.pub, layoutTest1)
        self.checkOwnLayout(self.pub, layoutTest1)
        self.pub.set_layout(layoutTest2['name'])
        self.checkLayout(self.pub, layoutTest2)
        self.checkOwnLayout(self.pub, layoutTest2)

    def testSubPublication(self):
        self.root.set_layout(layoutTest2['name'])
        self.checkLayout(self.pub, layoutTest2) 
        self.checkNoOwnLayout(self.pub)
        self.add_publication(self.pub, 'subpub', 'subpublication')
        self.failUnless(self.pub.subpub)
        self.subpub = self.pub.subpub
        self.checkLayout(self.subpub, layoutTest2) 
        self.checkNoOwnLayout(self.subpub)
        self.pub.set_layout(layoutTest1['name'])
        self.checkLayout(self.subpub, layoutTest1) 
        self.checkNoOwnLayout(self.subpub)
        self.subpub.set_layout(layoutTest2['name'])
        self.checkLayout(self.subpub, layoutTest2)
        self.checkOwnLayout(self.subpub, layoutTest2)
        self.subpub.set_layout(layoutTest1['name'])
        self.checkLayout(self.subpub, layoutTest1) 
        self.checkOwnLayout(self.subpub, layoutTest1)
        self.root.set_layout('')
        self.pub.set_layout('')
        self.subpub.set_layout('')
        self.checkNoLayout(self.subpub)
        self.checkNoOwnLayout(self.subpub)
        
    def testLayoutCopiedInSubPublication(self):
        self.pub.set_layout(layoutTest1['name'])
        self.checkLayout(self.pub, layoutTest1) 
        self.add_publication(self.pub, 'subpub', 'subpublication')
        self.failUnless(self.pub.subpub)
        self.subpub = self.pub.subpub
        self.checkLayout(self.subpub, layoutTest1) 
        self.checkNoOwnLayout(self.subpub)
        self.service_layouts.copy_layout(self.subpub)
        self.failIf(self.service_layouts.layout_copied(self.pub), 'Layout should not have been copied !')
        self.failUnless(self.service_layouts.layout_copied(self.subpub), 'Layout should have been copied !')
        self.checkOwnLayout(self.subpub, layoutTest1)
        self.service_layouts.remove_layout(self.subpub)
        self.checkCopiedLayoutTest1Removed(self.subpub)

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

