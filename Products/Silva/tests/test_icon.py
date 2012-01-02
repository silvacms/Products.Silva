# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import unittest

# Silva
from silva.core import interfaces
from zope.component import queryAdapter
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest
from silva.core.interfaces.adapters import IIconResolver


from Products.Silva.icon import IconRegistry, registry
from Products.Silva.testing import FunctionalLayer


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

    def test_get_icon_url(self):
        """Test usefull function get_icon_url
        """
        resolver = queryAdapter(TestRequest(), IIconResolver)
        self.assertTrue(verifyObject(IIconResolver, resolver))

        self.assertEqual(
            resolver.get_content(self.root),
            '++resource++icon-Silva-Root.png')
        self.assertEqual(
            resolver.get_content_url(self.root),
            'http://localhost/root/++resource++icon-Silva-Root.png')

        self.assertEqual(
            resolver.get_content(self.root.pdf),
            '++resource++silva.icons/file_pdf.png')
        self.assertEqual(
            resolver.get_content_url(self.root.pdf),
            'http://localhost/root/++resource++silva.icons/file_pdf.png')
        self.assertEqual(
            resolver.get_content(self.root.text),
            '++resource++silva.icons/file_txt.png')
        self.assertEqual(
            resolver.get_content_url(self.root.text),
            'http://localhost/root/++resource++silva.icons/file_txt.png')


    def test_default_icons(self):
        """Test default registered icons.
        """
        # Silva content types
        self.assertEqual(
            registry.get_icon(self.root),
            '++resource++icon-Silva-Root.png')
        self.assertEqual(
            registry.get_icon_by_identifier(
                ('meta_type', 'Silva Link')),
            '++resource++icon-Silva-Link.png' )

        # Simple member icons
        member = self.root.service_members.get_member('author')
        self.assertEqual(
            registry.get_icon(member),
            '++resource++icon-Silva-Simple-Member.png')

        # File icons
        self.assertEqual(
            registry.get_icon(self.root.pdf),
            '++resource++silva.icons/file_pdf.png')
        self.assertEqual(
            registry.get_icon(self.root.text),
            '++resource++silva.icons/file_txt.png')

    def test_registry(self):
        """Test registry
        """
        self.assertEquals(
            self.root.pdf.get_mime_type(), 'application/pdf')
        self.assertEquals(
            self.root.text.get_mime_type(), 'text/plain')

        registry = IconRegistry()
        self.failUnless(verifyObject(interfaces.IIconRegistry, registry))

        registry.register(
            ('meta_type', 'Silva Root'), 'root.png')
        registry.register(
            ('mime_type', 'text/plain'), 'file_text.png')
        registry.register(
            ('mime_type', 'application/octet-stream'), 'file.png')
        registry.register(
            ('mime_type', 'application/pdf'), 'file_pdf.png')

        self.assertEquals(
            registry.get_icon_by_identifier(
                ('meta_type', 'Silva Root')),
            'root.png')
        self.assertEquals(
            registry.get_icon_by_identifier(
                ('mime_type', 'application/octet-stream')),
            'file.png')
        self.assertRaises(
            ValueError, registry.get_icon_by_identifier,
            ('meta_type', 'Foo Bar'))

        self.assertEquals(registry.get_icon(self.root), 'root.png')
        self.assertEquals(registry.get_icon(self.root.pdf), 'file_pdf.png')
        self.assertEquals(registry.get_icon(self.root.text), 'file_text.png')
        self.assertRaises(ValueError, registry.get_icon, TestRequest())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IconRegistryTestCase))
    return suite

