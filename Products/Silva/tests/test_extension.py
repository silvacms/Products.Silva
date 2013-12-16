# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from urllib import URLopener
import unittest

from silva.core.conf.installer import SystemExtensionInstaller
from silva.core.interfaces.extension import IExtension, IExtensionInstaller
from silva.core.interfaces.extension import IExtensionRegistry
from silva.core.services.interfaces import IExtensionService
from zope.component import getUtility
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer
from Products.Silva.ExtensionRegistry import extensionRegistry


class ExtensionRegistryTestCase(unittest.TestCase):
    """Test extension registry/service
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_registry(self):
        # Check that the registry implements it's interface
        self.assertTrue(verifyObject(IExtensionRegistry, extensionRegistry))

        # Test get_name_for_class.
        from Products.Silva.Link import Link
        self.assertEquals(extensionRegistry.get_name_for_class(Link), 'Silva')
        self.assertEquals(extensionRegistry.get_name_for_class(URLopener), None)

    def test_extension_broken(self):
        # If you ask an unknown extension, you will get None
        extension = extensionRegistry.get_extension('SilvaInvalidExtension')
        self.assertEqual(extension, None)

    def test_extension_product(self):
        extension = extensionRegistry.get_extension('Silva')
        self.assertNotEqual(extension, None)

        self.assertTrue(verifyObject(IExtension, extension))
        self.assertEqual(extension.name, 'Silva')
        self.assertEqual(extension.title, 'Silva Core')
        self.assertEqual(extension.product, 'Silva')
        self.assertEqual(extension.module_name, 'Products.Silva')
        self.assertEqual(
            extension.description,
            'Silva Content Management System')

        self.assertEqual(
            [c['name'] for c in extension.get_content()],
            ['Silva AutoTOC',
             'Silva Container Policy Registry',
             'Silva Message Service',
             'Silva Extension Service',
             'Silva File',
             'Silva Files Service',
             'Silva Folder',
             'Silva Ghost',
             'Silva Ghost Version',
             'Silva Ghost Asset',
             'Silva Ghost Folder',
             'Silva Image',
             'Silva Indexer',
             'Silva Link',
             'Silva Link Version',
             'Silva Publication',
             'Silva Root',
             'Silva Simple Member',
             'Silva Filtering Service',
             'Mockup Asset',
             'Mockup Non Publishable',
             'Mockup VersionedContent',
             'Mockup Version'])
        self.assertEqual(
            [c['product'] for c in extension.get_content()],
            ['Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva',
             'Silva'])

    def test_extension_egg(self):
        extension = extensionRegistry.get_extension('silva.core.layout')
        self.assertNotEqual(extension, None)

        self.assertTrue(verifyObject(IExtension, extension))
        self.assertEqual(extension.name, 'silva.core.layout')
        self.assertEqual(extension.title, 'Silva Core Layout')
        self.assertEqual(extension.product, 'silva.core.layout')
        self.assertEqual(extension.module_name, 'silva.core.layout')
        self.assertEqual(
            extension.description,
            'Layout and theme engine for Silva CMS')

    def test_installer(self):
        # First system extension installer.
        system_installer = SystemExtensionInstaller()
        self.assertTrue(verifyObject(IExtensionInstaller, system_installer))
        # A system extension is always installed
        self.assertEqual(
            system_installer.is_installed(self.root, object()),
            True)

        # Other test on installer are done with grok tests.


class ExtensionServiceTestCase(unittest.TestCase):
    """Test extension registry/service
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('extra', 'Extra')
        factory.manage_addMockupVersionedContent('contact', 'Contact')

    def test_implementation(self):
        service = getUtility(IExtensionService)
        self.assertTrue(verifyObject(IExtensionService, service))

    def test_reindex(self):
        service = getUtility(IExtensionService)
        service.reindex_all()

    def test_reindex_partial(self):
        service = getUtility(IExtensionService)
        service.reindex_subtree('/')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExtensionRegistryTestCase))
    suite.addTest(unittest.makeSuite(ExtensionServiceTestCase))
    return suite
