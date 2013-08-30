# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Python
import unittest

from silva.core.interfaces import IIconRegistry, IIconResolver, IIcon
from zope.component import queryAdapter
from zope.interface.verify import verifyObject

from Products.Silva.icon import registry
from Products.Silva.testing import FunctionalLayer, TestRequest


class IconRegistryTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFile('pdf', 'PDF File')
        factory.manage_addFile('text', 'Text File')
        self.root.pdf.set_content_type('application/pdf')
        self.root.text.set_content_type('text/plain')

    def test_icon_resolver(self):
        """Test adapter to retrieve icon urls'.
        """
        resolver = queryAdapter(TestRequest(), IIconResolver)
        self.assertTrue(verifyObject(IIconResolver, resolver))

        icon = resolver.get_content(self.root)
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(
            str(icon),
            '++resource++icon-Silva-Root.png')
        icon = resolver.get_identifier('Silva Root')
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(
            str(icon),
            '++resource++icon-Silva-Root.png')
        icon = resolver.get_identifier(None) # Missing
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(
            str(icon),
            '++static++/silva.icons/missing.png')
        icon = resolver.get_identifier('Best content in the world') # Generic
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(
            str(icon),
            '++static++/silva.icons/generic.png')

        self.assertEqual(
            resolver.get_content_url(self.root),
            'http://localhost/root/++resource++icon-Silva-Root.png')
        self.assertEqual(
            resolver.get_content_url(None),
            'http://localhost/root/++static++/silva.icons/missing.png')
        self.assertEqual(
            resolver.get_identifier_url('Silva Root'),
            'http://localhost/root/++resource++icon-Silva-Root.png')
        self.assertEqual(
            resolver.get_identifier_url(None),
            'http://localhost/root/++static++/silva.icons/missing.png')
        self.assertEqual(
            resolver.get_identifier_url('best content in the world'),
            'http://localhost/root/++static++/silva.icons/generic.png')

        icon = resolver.get_content(self.root.pdf)
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(
            str(icon),
            '++static++/silva.icons/file_pdf.png')
        icon = resolver.get_content(self.root.text)
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(
            str(icon),
            '++static++/silva.icons/file_txt.png')

        self.assertEqual(
            resolver.get_content_url(self.root.pdf),
            'http://localhost/root/++static++/silva.icons/file_pdf.png')
        self.assertEqual(
            resolver.get_content_url(self.root.text),
            'http://localhost/root/++static++/silva.icons/file_txt.png')

    def test_icon_tag(self):
        """Test usefull function used to access icon tags.
        """
        resolver = queryAdapter(TestRequest(), IIconResolver)
        self.assertTrue(verifyObject(IIconResolver, resolver))

        self.assertEqual(
            resolver.get_tag(self.root),
            '<img height="16" width="16" src="http://localhost/root/++resource++icon-Silva-Root.png" alt="Silva Root" />')
        self.assertEqual(
            resolver.get_tag(content=self.root),
            '<img height="16" width="16" src="http://localhost/root/++resource++icon-Silva-Root.png" alt="Silva Root" />')
        self.assertEqual(
            resolver.get_tag(identifier='Silva Root'),
            '<img height="16" width="16" src="http://localhost/root/++resource++icon-Silva-Root.png" alt="Silva Root" />')
        self.assertEqual(
            resolver.get_tag(identifier='default'),
            '<img height="16" width="16" src="http://localhost/root/++static++/silva.icons/generic.png" alt="default" />')
        self.assertEqual(
            resolver.get_tag(),
            '<img height="16" width="16" src="http://localhost/root/++static++/silva.icons/missing.png" alt="Missing" />')

    def test_custom_icons(self):
        """Test registring icons with a custom namespace and looking
        them up.
        """
        registry.register(('test-silva', 'model'), '++custom++foo.png')
        registry.register(('test-silva', 'page'), '++custom++bar.jpeg')
        registry.register(('default', 'test-silva'), '++custom++empty.gif')

        resolver = queryAdapter(TestRequest(), IIconResolver)
        self.assertTrue(verifyObject(IIconResolver, resolver))

        icon = resolver.get_identifier(('test-silva', 'model'))
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(str(icon), '++custom++foo.png')
        self.assertEqual(
            resolver.get_identifier_url(('test-silva', 'model')),
            'http://localhost/root/++custom++foo.png')

        icon = resolver.get_identifier(('test-silva', 'missing'))
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(str(icon), '++static++/silva.icons/generic.png')
        self.assertEqual(
            resolver.get_identifier_url(('test-silva', 'missing')),
            'http://localhost/root/++static++/silva.icons/generic.png')

        icon = resolver.get_identifier(
            ('test-silva', 'missing'), default='test-silva')
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(str(icon), '++custom++empty.gif')
        self.assertEqual(
            resolver.get_identifier_url(
                ('test-silva', 'missing'), default='test-silva'),
            'http://localhost/root/++custom++empty.gif')

        icon = resolver.get_identifier(
            ('test-silva', 'missing'), default=('test-silva', 'page'))
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(str(icon), '++custom++bar.jpeg')
        self.assertEqual(
            resolver.get_identifier_url(
                ('test-silva', 'missing'), default=('test-silva', 'page')),
            'http://localhost/root/++custom++bar.jpeg')

        icon = resolver.get_identifier(
            ('test-silva', 'missing'), default=('test-silva', 'metoo'))
        self.assertIs(icon, None)
        self.assertIs(
            resolver.get_identifier_url(
                ('test-silva', 'missing'), default=('test-silva', 'metoo')),
            None)

    def test_default_icons(self):
        """Test default registered icons.
        """
        self.assertTrue(verifyObject(IIconRegistry, registry))

        icon = registry.get(('meta_type', 'Silva Link'))
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(
            str(icon),
            '++resource++icon-Silva-Link.png' )

        icon = registry.get(('meta_type', 'Silva Simple Member'))
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(
            str(icon),
            '++resource++icon-Silva-Simple-Member.png')

        icon = registry.get(('mime_type', 'application/pdf'))
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(
            str(icon),
            '++static++/silva.icons/file_pdf.png')

        icon = registry.get(('mime_type', 'text/plain'))
        self.assertTrue(verifyObject(IIcon, icon))
        self.assertEqual(
            str(icon),
            '++static++/silva.icons/file_txt.png')

        with self.assertRaises(ValueError):
            registry.get(('meta_type', 'Best content in the world'))

        marker = object()
        icon = registry.get(
            ('meta_type', 'Best content in the world'),
            default=marker)
        self.assertIs(icon, marker)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IconRegistryTestCase))
    return suite

