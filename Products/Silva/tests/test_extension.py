# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from urllib import URLopener
import unittest

from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer
from Products.Silva.ExtensionRegistry import extensionRegistry
from silva.core.interfaces.extension import (
    IExtensionRegistry, IExtension, IExtensionInstaller)

from silva.core.conf.installer import SystemExtensionInstaller
from silva.core.conf.registry import getRegistry


class ExtensionRegistryTestCase(unittest.TestCase):
    """Test extension registry/service
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_registry(self):
        # We can get the registry using the registry API
        self.assertEquals(extensionRegistry, getRegistry('extensionregistry'))

        # Check that the registry implements it's interface
        self.failUnless(verifyObject(IExtensionRegistry, extensionRegistry))

        # Test get_names. SilvaDocument is installed by default.
        self.failUnless('SilvaDocument' in extensionRegistry.get_names())

        # Test is_installed. By default those extension are installed.
        self.assertEquals(
            extensionRegistry.is_installed('SilvaDocument', self.root),
            True)
        self.assertEquals(
            extensionRegistry.is_installed('SilvaExternalSources', self.root),
            True)

        # Test get_name_for_class.
        from Products.SilvaDocument.Document import Document
        self.assertEquals(
            extensionRegistry.get_name_for_class(Document),
            'SilvaDocument')
        from Products.Silva.Link import Link
        self.assertEquals(extensionRegistry.get_name_for_class(Link), 'Silva')
        self.assertEquals(extensionRegistry.get_name_for_class(URLopener), None)

    def test_extension_broken(self):
        # If you ask an unknown extension, you will get None
        extension = extensionRegistry.get_extension('SilvaInvalidExtension')
        self.assertEqual(extension, None)

    def test_extension_product(self):
        extension = extensionRegistry.get_extension('SilvaDocument')
        self.assertNotEqual(extension, None)

        self.failUnless(verifyObject(IExtension, extension))
        self.assertEqual(extension.name, 'SilvaDocument')
        self.assertEqual(extension.description, 'Silva Document')
        self.assertEqual(extension.product, 'SilvaDocument')
        self.assertEqual(extension.module_name, 'Products.SilvaDocument')

        self.assertEqual([c['name'] for c in extension.get_content()],
                         ['Silva Document', 'Silva Document Version'])
        self.assertEqual([c['product'] for c in extension.get_content()],
                         ['SilvaDocument', 'SilvaDocument'])

    def test_extension_egg(self):
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


class ExtensionServiceTestCase(unittest.TestCase):
    """Test extension registry/service
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_reindex(self):
        # Empty reindexing.
        self.root.service_extensions.reindex_all()

        # Add some content:
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('documentation', 'Documentation')
        factory.manage_addDocument('extra', 'Extra')
        factory.manage_addDocument('contact', 'Contact')

        # Reindex new content.
        self.root.service_extensions.reindex_all()

    def test_reindex_partial(self):
        self.root.service_extensions.reindex_subtree('/')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExtensionRegistryTestCase))
    suite.addTest(unittest.makeSuite(ExtensionServiceTestCase))
    return suite
