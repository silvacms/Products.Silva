# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface.verify import verifyObject

from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.interfaces.extension import IExtensionRegistry, IExtension, IExtensionInstaller

from silva.core.conf.installer import DefaultInstaller, SystemExtensionInstaller

import SilvaTestCase


class ExtensionRegistryTest(SilvaTestCase.SilvaTestCase):
    
    def test_registry(self):
        # Check that the registry implements it's interface
        self.failUnless(verifyObject(IExtensionRegistry, extensionRegistry))

        # Test get_names. SilvaDocument is installed by default.
        self.failUnless('SilvaDocument' in extensionRegistry.get_names())

        # Test is_installed.
        self.assertEquals(extensionRegistry.is_installed('SilvaDocument', self.root), True)
        self.assertEquals(extensionRegistry.is_installed('SilvaExternalSources', self.root), False)

        # Test get_name_for_class.
        from Products.SilvaDocument.Document import Document
        self.assertEquals(extensionRegistry.get_name_for_class(Document), 'SilvaDocument')
        from Products.Silva.Link import Link
        self.assertEquals(extensionRegistry.get_name_for_class(Link), 'Silva')
        from urllib import URLopener
        self.assertEquals(extensionRegistry.get_name_for_class(URLopener), None)

    def test_extension(self):
        # If you ask an unknown extension, you will get None
        extension = extensionRegistry.get_extension('SilvaInvalidExtension')
        self.assertEqual(extension, None)

        # If you ask a known extension, you will get one.
        # First, a zope product.
        extension = extensionRegistry.get_extension('SilvaDocument')
        self.assertNotEqual(extension, None)

        self.failUnless(verifyObject(IExtension, extension))
        self.assertEqual(extension.name, 'SilvaDocument')
        self.assertEqual(extension.description, 'Silva Document')
        self.assertEqual(extension.product, 'SilvaDocument')
        self.assertEqual(extension.module_name, 'Products.SilvaDocument')
        
        contents = extension.get_content()
        self.assertEqual([c['name'] for c in extension.get_content()],
                         ['Silva Document', 'Silva Document Version', 
                          'Silva Editor Support Service', 'Silva CodeSource Charset Service'])
        self.assertEqual([c['product'] for c in extension.get_content()],
                         ['SilvaDocument', 'SilvaDocument', 'SilvaDocument', 'SilvaDocument'])
        
        # After, an egg.
        extension = extensionRegistry.get_extension('silva.core.layout')
        self.assertNotEqual(extension, None)

        self.failUnless(verifyObject(IExtension, extension))
        self.assertEqual(extension.name, 'silva.core.layout')
        self.assertEqual(extension.description, 'Silva Core Layout')
        self.assertEqual(extension.product, 'silva.core.layout')
        self.assertEqual(extension.module_name, 'silva.core.layout')
        

    def test_installer(self):
        # First system extension installer.
        system_installer = SystemExtensionInstaller()
        self.failUnless(verifyObject(IExtensionInstaller, system_installer))
        # A system extension is always installed
        self.assertEqual(system_installer.is_installed(self.root), True)

        # Other test on installer are done with grok tests.


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExtensionRegistryTest))
    return suite

